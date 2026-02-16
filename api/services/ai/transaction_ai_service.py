from sqlalchemy.orm import Session
from models.models import ExpenseCategory, IncomeCategory, InvestmentCategory
class TransactionAIService:

    def __init__(self, db: Session):
        self.db = db

    def classify(self, transactions: list[dict]) -> list[dict]:
        results = []

        for tx in transactions:
            category_id = self._classify_single(tx)
            results.append({
                "id": tx["id"],
                "category_id": category_id
            })

        return results
