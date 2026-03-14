from sqlalchemy import select
from sqlalchemy.orm import Session
from models.expenses.expense_category_model import ExpensesCategory
from models.incomes.income_category_model import IncomesCategory
from models.investments.investment_category_model import InvestmentsCategory
import urllib.request
import urllib.error
import json
import re
import unicodedata

from services.logs.logger_service import setup_logger
logger = setup_logger("transaction_ai")


class TransactionAIService:

    def __init__(self, db: Session):
        # Guardamos la sesión de base de datos para usarla en las consultas
        self.db = db

    # ─────────────────────────────────────────────
    # MÉTODO PRINCIPAL
    # Recibe las transacciones y las reglas del frontend
    # Devuelve cada transacción con su categoría asignada o sugerida
    # ─────────────────────────────────────────────
    def classify(self, transactions: list[dict], rules: list[dict]) -> list[dict]:
        rules = rules or []
        if not transactions:
            return []

        # 1. Cargamos todas las categorías de la base de datos agrupadas por tipo
        categories_by_type = {
            "expense": self._get_categories("expense"),
            "income": self._get_categories("income"),
            "investment": self._get_categories("investment")
        }

        # Aquí guardaremos las predicciones indexadas por el id de la transacción
        predictions_by_id = {}

        # Transacciones que no matchearon con las rules y hay que enviar a la IA
        transactions_by_type: dict[str, list[dict]] = {
            "expense": [],
            "income": [],
            "investment": []
        }

        # 2. Primera pasada: intentamos categorizar con las rules del frontend
        for tx in transactions:
            type_ = tx.get("type")
            tx_id = tx.get("id")
            categories = categories_by_type.get(type_)

            # Si no tiene tipo o no hay categorías para ese tipo, la ignoramos
            if tx_id is None or not categories:
                continue

            # Intentamos hacer match con las rules (ej: "mercadona" → Supermercado)
            merchant_match = self._match_known_patterns(tx, categories, type_, rules)

            if merchant_match:
                # Match encontrado → la guardamos directamente, no va a la IA
                predictions_by_id[tx_id] = merchant_match
            else:
                # Sin match → la añadimos a la lista para enviar a la IA
                transactions_by_type[type_].append(tx)

        # 3. Segunda pasada: enviamos a la IA las que no matchearon
        for type_, txs in transactions_by_type.items():
            if not txs:
                continue

            categories = categories_by_type[type_]
            try:
                ai_predictions = self._classify_batch(type_, txs, categories)
            except Exception as exc:
                logger.exception(
                    "Fallo en clasificación IA para type=%s con %s transacciones.",
                    type_, len(txs), exc_info=exc,
                )
                ai_predictions = {}

            predictions_by_id.update(ai_predictions)

        # 4. Construimos el resultado final con todas las transacciones
        # Si no se encontró predicción, category será None
        return [
            {
                "id": tx.get("id"),
                "category": predictions_by_id.get(tx.get("id")),
            }
            for tx in transactions
        ]

    # ─────────────────────────────────────────────
    # CONSULTA DE CATEGORÍAS EN BASE DE DATOS
    # Devuelve las categorías activas (sin deleted_at) según el tipo
    # ─────────────────────────────────────────────
    def _get_categories(self, type_: str) -> list:
        if type_ == "expense":
            stmt = select(ExpensesCategory).where(ExpensesCategory.deleted_at.is_(None))
            categories = list(self.db.execute(stmt).scalars().all())
            logger.debug(f"Categorías de gasto: {[c.name for c in categories]}")
            return categories

        if type_ == "income":
            stmt = select(IncomesCategory).where(IncomesCategory.deleted_at.is_(None))
            categories = list(self.db.execute(stmt).scalars().all())
            logger.debug(f"Categorías de ingreso: {[c.name for c in categories]}")
            return categories

        if type_ == "investment":
            stmt = select(InvestmentsCategory).where(InvestmentsCategory.deleted_at.is_(None))
            categories = list(self.db.execute(stmt).scalars().all())
            logger.debug(f"Categorías de inversión: {[c.name for c in categories]}")
            return categories

        return []

    # ─────────────────────────────────────────────
    # CLASIFICACIÓN POR IA
    # Envía un lote de transacciones al modelo de IA local
    # Le pasamos las categorías disponibles para que elija entre ellas
    # Si no hay match, pedimos que sugiera una categoría nueva
    # ─────────────────────────────────────────────
    def _classify_batch(self, type_: str, transactions: list[dict], categories: list) -> dict:

        # Preparamos las categorías disponibles para pasárselas a la IA
        categories_payload = [
            {"name": c.name, "description": getattr(c, "description", "")}
            for c in categories
        ]

        # Preparamos las transacciones con solo los campos relevantes
        tx_payload = [
            {
                "id": tx.get("id"),
                "description": tx.get("description"),
                "amount": tx.get("amount"),
            }
            for tx in transactions
        ]

        # Prompt que le enviamos a la IA con instrucciones claras
        prompt = f"""
                  You are a financial transaction classifier.
                  Type: {type_}
                  Transactions: {json.dumps(tx_payload, ensure_ascii=False)}
                  Available categories: {json.dumps(categories_payload, ensure_ascii=False)}

                Rules:
                    - Only use an existing category if it clearly fits the transaction.
                    - Do not force a category if it does not match well.
                    - If no category fits, set category to null and suggest a new category.

                    Suggested category rules:
                    - Must be a GENERIC expense category.
                    - Must NOT contain merchant names.
                    - Must NOT contain cities or locations.
                    - Use short names (1-3 words).

                    Examples of valid suggestions:
                    Salud
                    Farmacia
                    Parking
                    Peajes
                    Gimnasio
                    Mascotas
                    Veterinario
                    Ocio

                Good examples:

                    Transaction: FARMACIA GARCIA
                    Result:
                    {{"id":1,"category":null,"suggested_new_category":"Farmacia"}}

                    Transaction: PARKING PLAZA MAYOR
                    Result:
                    {{"id":1,"category":null,"suggested_new_category":"Parking"}}

                    Transaction: CLINICA DENTAL
                    Result:
                    {{"id":1,"category":null,"suggested_new_category":"Salud"}}

                    Return ONLY JSON in this format:
                    {{"classifications":[{{"id":"...","category":"..." | null,"suggested_new_category":"..." | null}}]}}


                  Return only valid JSON with this schema:
                  {{"classifications":[{{"id":"...","category":"..." | null,"suggested_new_category":"..." | null}}]}}
                  """

        # Payload completo para la API del modelo de IA (formato OpenAI compatible)
        payload = {
            "messages": [
                # El rol system define el comportamiento general del modelo
                {"role": "system", "content": "You are a strict financial classifier. Return only JSON."},
                # El rol user es el prompt con los datos reales
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,  # 0 = respuestas más deterministas, sin creatividad
            "max_tokens": max(120, len(transactions) * 40)  # tokens proporcionales al número de transacciones
        }

        # Construimos la petición HTTP al servidor de IA local
        req = urllib.request.Request(
            "http://ai:8180/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        # Enviamos la petición y leemos la respuesta
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            logger.warning("Servicio de IA no disponible: %s", exc)
            return {}

        # Extraemos el texto de la respuesta del modelo
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Intentamos parsear el JSON directamente
        # A veces la IA añade texto extra o bloques ```json ... ```, así que
        # si falla el parse directo, buscamos el JSON con una expresión regular
        try:
            parsed = json.loads(content)
        except Exception:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group())
                except Exception:
                    logger.warning("No se pudo extraer JSON de la respuesta IA: %s", content)
                    return {}
            else:
                logger.warning("No se encontró JSON en la respuesta IA: %s", content)
                return {}

        # Creamos un diccionario de categorías normalizadas para hacer lookup rápido
        # clave: nombre normalizado (sin tildes, minúsculas) → valor: objeto categoría
        category_by_name = {self._normalize_text(c.name): c for c in categories}
        predictions = {}

        # Procesamos cada clasificación que devolvió la IA
        for item in parsed.get("classifications", []):
            tx_id = item.get("id")
            category_name = item.get("category")
            suggested = item.get("suggested_new_category")

            if tx_id is None:
                continue

            if category_name:
                # La IA propuso una categoría existente → buscamos en BD
                matched = category_by_name.get(self._normalize_text(str(category_name)))
                if matched:
                    predictions[tx_id] = {
                        "id": matched.id,
                        "name": matched.name,
                        "description": getattr(matched, "description", None),
                        "suggested_new_category": None  # tiene categoría real, no necesita sugerencia
                    }
                    continue

            # La IA no encontró categoría existente → guardamos la sugerencia de nueva categoría
            predictions[tx_id] = {
                "id": None,
                "name": None,
                "description": None,
                "suggested_new_category": suggested  # ej: "Peajes", "Gimnasio", "Farmacia"
            }

        return predictions

    # ─────────────────────────────────────────────
    # MATCH POR RULES DEL FRONTEND
    # Antes de llamar a la IA, intentamos clasificar con las reglas
    # que vienen del frontend (CATEGORY_RULES de Angular)
    # Ejemplo: si la descripción contiene "mercadona" → categoría "Supermercado"
    # ─────────────────────────────────────────────
    def _match_known_patterns(self, tx: dict, categories: list, type_: str, rules: list[dict]):
        # Normalizamos la descripción para comparar sin tildes ni mayúsculas
        description = self._normalize_text(tx.get("description", ""))

        for rule in rules:
            # Solo procesamos rules del mismo tipo (expense, income, investment)
            if rule.get("type") != type_:
                continue

            # Normalizamos las keywords de la rule
            keywords = [self._normalize_text(k) for k in rule.get("keywords", [])]

            # Comprobamos si alguna keyword aparece en la descripción
            if not any(kw in description for kw in keywords):
                continue

            # Keyword encontrada → buscamos la categoría por nombre exacto en BD
            category_name = self._normalize_text(rule.get("categoryName", ""))
            matched = next(
                (c for c in categories if self._normalize_text(c.name) == category_name),
                None
            )

            if matched:
                return {
                    "id": matched.id,
                    "name": matched.name,
                    "description": getattr(matched, "description", None),
                    "suggested_new_category": None
                }

        # Ninguna rule coincidió
        return None

    # ─────────────────────────────────────────────
    # NORMALIZACIÓN DE TEXTO
    # Elimina tildes y convierte a minúsculas para comparar textos
    # Ejemplo: "Ñoño" → "nono", "Ámsterdam" → "amsterdam"
    # ─────────────────────────────────────────────
    def _normalize_text(self, text: str) -> str:
        # NFKD descompone los caracteres con tilde en letra + diacrítico separados
        normalized = unicodedata.normalize("NFKD", str(text))
        # Filtramos los diacríticos (tildes, cedillas, etc.) y pasamos a minúsculas
        return "".join(c for c in normalized if not unicodedata.combining(c)).strip().lower()