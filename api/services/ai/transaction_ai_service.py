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
        # Comment translated to English.
        self.db = db

    # ─────────────────────────────────────────────
    # Comment translated to English.
    # Comment translated to English.
    # Comment translated to English.
    # ─────────────────────────────────────────────
    def classify(self, transactions: list[dict], rules: list[dict]) -> list[dict]:
        rules = rules or []
        if not transactions:
            return []

        # Comment translated to English.
        categories_by_type = {
            "expense": self._get_categories("expense"),
            "income": self._get_categories("income"),
            "investment": self._get_categories("investment")
        }

        # Comment translated to English.
        predictions_by_id = {}

        # Comment translated to English.
        transactions_by_type: dict[str, list[dict]] = {
            "expense": [],
            "income": [],
            "investment": []
        }

        # Comment translated to English.
        for tx in transactions:
            type_ = tx.get("type")
            tx_id = tx.get("id")
            categories = categories_by_type.get(type_)

            # Comment translated to English.
            if tx_id is None or not categories:
                continue

            # Comment translated to English.
            merchant_match = self._match_known_patterns(tx, categories, type_, rules)

            if merchant_match:
                # Match encontrado → la guardamos directamente, no va a la IA
                predictions_by_id[tx_id] = merchant_match
            else:
                # Comment translated to English.
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

        # Comment translated to English.
        # Comment translated to English.
        return [
            {
                "id": tx.get("id"),
                "category": predictions_by_id.get(tx.get("id")),
            }
            for tx in transactions
        ]

    # ─────────────────────────────────────────────
    # Comment translated to English.
    # Comment translated to English.
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
    # Comment translated to English.
    # Comment translated to English.
    # Comment translated to English.
    # Comment translated to English.
    # ─────────────────────────────────────────────
    def _classify_batch(self, type_: str, transactions: list[dict], categories: list) -> dict:

        # Comment translated to English.
        categories_payload = [
            {"name": c.name, "description": getattr(c, "description", "")}
            for c in categories
        ]

        # Comment translated to English.
        tx_payload = [
            {
                "id": tx.get("id"),
                "description": tx.get("description"),
                "amount": tx.get("amount"),
            }
            for tx in transactions
        ]

        # Comment translated to English.
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

        # Comment translated to English.
        payload = {
            "messages": [
                # El rol system define el comportamiento general del modelo
                {"role": "system", "content": "You are a strict financial classifier. Return only JSON."},
                # Comment translated to English.
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,  # Comment translated to English.
            "max_tokens": max(120, len(transactions) * 40)  # Comment translated to English.
        }

        # Comment translated to English.
        req = urllib.request.Request(
            "http://ai:8180/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        # Send request and parse response
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            logger.warning("Servicio de IA no disponible: %s", exc)
            return {}

        # Extract model text response
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Try direct JSON parsing first.
        # Sometimes the AI adds extra text or ```json ... ``` wrappers,
        # so if direct parsing fails, try extracting JSON with regex.
        try:
            parsed = json.loads(content)
        except Exception:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group())
                except Exception:
                    logger.warning("Could not extract JSON from AI response: %s", content)
                    return {}
            else:
                logger.warning("No JSON found in AI response: %s", content)
                return {}

        # Build normalized category lookup map:
        # key: normalized name (no accents/lowercase) -> value: category object
        category_by_name = {self._normalize_text(c.name): c for c in categories}
        predictions = {}

        # Process each AI classification
        for item in parsed.get("classifications", []):
            tx_id = item.get("id")
            category_name = item.get("category")
            suggested = item.get("suggested_new_category")

            if tx_id is None:
                continue

            if category_name:
                # AI proposed an existing category -> resolve against DB categories
                matched = category_by_name.get(self._normalize_text(str(category_name)))
                if matched:
                    predictions[tx_id] = {
                        "id": matched.id,
                        "name": matched.name,
                        "description": getattr(matched, "description", None),
                        "suggested_new_category": None  # has a real category, no suggestion needed
                    }
                    continue

            # AI did not match an existing category -> keep suggested new category
            predictions[tx_id] = {
                "id": None,
                "name": None,
                "description": None,
                "suggested_new_category": suggested  # e.g. "Tolls", "Gym", "Pharmacy"
            }

        return predictions

    # ─────────────────────────────────────────────
    # MATCH USING FRONTEND RULES
    # Before calling AI, try classification using rules
    # sent by frontend (Angular CATEGORY_RULES).
    # Example: if description contains "mercadona" -> "Supermarket" category.
    # ─────────────────────────────────────────────
    def _match_known_patterns(self, tx: dict, categories: list, type_: str, rules: list[dict]):
        # Normalize description for accent/case-insensitive matching
        description = self._normalize_text(tx.get("description", ""))

        for rule in rules:
            # Only process rules with matching transaction type (expense, income, investment)
            if rule.get("type") != type_:
                continue

            # Normalize rule keywords
            keywords = [self._normalize_text(k) for k in rule.get("keywords", [])]

            # Check if any keyword is present in description
            if not any(kw in description for kw in keywords):
                continue

            # Keyword found -> resolve category by normalized exact name in DB categories
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

        # Comment translated to English.
        return None

    # ─────────────────────────────────────────────
    # Comment translated to English.
    # Comment translated to English.
    # Comment translated to English.
    # ─────────────────────────────────────────────
    def _normalize_text(self, text: str) -> str:
        # Comment translated to English.
        normalized = unicodedata.normalize("NFKD", str(text))
        # Comment translated to English.
        return "".join(c for c in normalized if not unicodedata.combining(c)).strip().lower()
