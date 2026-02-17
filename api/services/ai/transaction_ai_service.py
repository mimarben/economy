from sqlalchemy.orm import Session
from models.expenses.expense_category_model import ExpensesCategory
from models.incomes.income_category_model import IncomesCategory
from models.investments.investment_category_model import InvestmentsCategory
import urllib.request
import json

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

    def _classify_single(self, tx: dict):

        type_ = tx.get("type")
        description = tx.get("description")
        amount = tx.get("amount")

        # 1️⃣ Obtener categorías según tipo
        if type_ == "expense":
            categories = self.db.query(ExpensesCategory).all()
            print(f"Expense categories: {[c.name for c in categories]}")
        elif type_ == "income":
            categories = self.db.query(IncomesCategory).all()
            print(f"Income categories: {[c.name for c in categories]}")
        elif type_ == "investment":
            categories = self.db.query(InvestmentsCategory).all()
            print(f"Investment categories: {[c.name for c in categories]}")
        else:
            return None

        category_names = [c.name for c in categories]

        # 2️⃣ Construir prompt
        prompt = f"""
                  Transaction:
                  Description: {description}
                  Amount: {amount}
                  Type: {type_}

                  Available categories:
                  {json.dumps(category_names)}

                  Return only valid JSON:
                  {{"category":"..."}}
                  """

        # 3️⃣ Llamar a llama.cpp
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
            "max_tokens": 50
        }
        req = urllib.request.Request(
            "http://ai:8180/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as response:
          result = json.loads(response.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
        try:
            parsed = json.loads(content)
            category_name = parsed.get("category")
        except Exception:
            return None

        # 4️⃣ Convertir nombre → id
        for c in categories:
          if c.name.lower() == (category_name or "").lower():
              return {
                  "id": c.id,
                  "name": c.name,
                  "description": getattr(c, "description", None)
              }
        return None
