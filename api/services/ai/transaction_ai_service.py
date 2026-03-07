from sqlalchemy import select
from sqlalchemy.orm import Session
from models.expenses.expense_category_model import ExpensesCategory
from models.incomes.income_category_model import IncomesCategory
from models.investments.investment_category_model import InvestmentsCategory
import urllib.request
import json
import unicodedata

# Setup logging
from services.logs.logger_service import setup_logger
logger = setup_logger("transaction_ai")


class TransactionAIService:

    def __init__(self, db: Session):
        self.db = db

    def classify(self, transactions: list[dict]) -> list[dict]:
        if not transactions:
            return []

        categories_by_type = {
            "expense": self._get_categories("expense"),
            "income": self._get_categories("income"),
            "investment": self._get_categories("investment")
        }

        predictions_by_id = {}
        transactions_by_type: dict[str, list[dict]] = {"expense": [], "income": [], "investment": []}

        for tx in transactions:
            type_ = tx.get("type")
            tx_id = tx.get("id")
            categories = categories_by_type.get(type_)

            if tx_id is None or not categories:
                continue

            merchant_match = self._match_known_merchant(tx, categories, type_)
            if merchant_match:
                predictions_by_id[tx_id] = merchant_match
                continue

            transactions_by_type[type_].append(tx)

        for type_, txs in transactions_by_type.items():
            if not txs:
                continue

            categories = categories_by_type[type_]
            ai_predictions = self._classify_batch(type_, txs, categories)
            predictions_by_id.update(ai_predictions)

        return [{"id": tx.get("id"), "category_id": predictions_by_id.get(tx.get("id"))} for tx in transactions]

    def _get_categories(self, type_: str) -> list:
        if type_ == "expense":
            stmt = select(ExpensesCategory).where(ExpensesCategory.deleted_at.is_(None))
            categories = list(self.db.execute(stmt).scalars().all())
            logger.debug(f"Expense categories: {[c.name for c in categories]}")
            return categories
        if type_ == "income":
            stmt = select(IncomesCategory).where(IncomesCategory.deleted_at.is_(None))
            categories = list(self.db.execute(stmt).scalars().all())
            logger.debug(f"Income categories: {[c.name for c in categories]}")
            return categories
        if type_ == "investment":
            stmt = select(InvestmentsCategory).where(InvestmentsCategory.deleted_at.is_(None))
            categories = list(self.db.execute(stmt).scalars().all())
            logger.debug(f"Investment categories: {[c.name for c in categories]}")
            return categories
        return []

    def _classify_batch(self, type_: str, transactions: list[dict], categories: list) -> dict:
        categories_payload = [
            {"name": c.name, "description": getattr(c, "description", "")}
            for c in categories
        ]
        tx_payload = [
            {
                "id": tx.get("id"),
                "description": tx.get("description"),
                "amount": tx.get("amount")
            }
            for tx in transactions
        ]

        prompt = f"""
                  Type: {type_}
                  Transactions: {json.dumps(tx_payload, ensure_ascii=False)}
                  Available categories: {json.dumps(categories_payload, ensure_ascii=False)}

                  Rules:
                  - Use only category names from available categories.
                  - If a merchant clearly maps to a category (example: Carrefour -> supermarket), prioritize that category.
                  - Return exactly one category per transaction id.

                  Return only valid JSON with this schema:
                  {{"classifications":[{{"id":"...","category":"..."}}]}}
                  """

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a strict financial classifier. Return only JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0,
            "max_tokens": max(120, len(transactions) * 40)
        }

        req = urllib.request.Request(
            "http://ai:8180/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))

        content = result["choices"][0]["message"]["content"]
        try:
            parsed = json.loads(content)
        except Exception:
            logger.warning(f"Invalid AI response for batch classification: {content}")
            return {}

        category_by_name = {self._normalize_text(c.name): c for c in categories}
        predictions = {}

        for item in parsed.get("classifications", []):
            tx_id = item.get("id")
            category_name = item.get("category")

            if tx_id is None or not category_name:
                continue

            matched = category_by_name.get(self._normalize_text(str(category_name)))
            if not matched:
                continue

            predictions[tx_id] = {
                "id": matched.id,
                "name": matched.name,
                "description": getattr(matched, "description", None)
            }

        return predictions

    def _match_known_merchant(self, tx: dict, categories: list, type_: str):
        if type_ != "expense":
            return None

        description = self._normalize_text(tx.get("description", ""))
        supermarket_merchants = ["carrefour", "mercadona", "lidl", "dia", "alcampo", "eroski"]
        is_supermarket_merchant = any(merchant in description for merchant in supermarket_merchants)

        if not is_supermarket_merchant:
            return None

        for category in categories:
            category_text = self._normalize_text(
                f"{category.name} {getattr(category, 'description', '')}"
            )
            if any(
                keyword in category_text
                for keyword in ["supermerc", "market", "grocery", "alimentacion", "comida"]
            ):
                return {
                    "id": category.id,
                    "name": category.name,
                    "description": getattr(category, "description", None)
                }

        return None

    def _normalize_text(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKD", str(text))
        return "".join(c for c in normalized if not unicodedata.combining(c)).strip().lower()
