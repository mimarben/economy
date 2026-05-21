"""Summary repository for aggregation queries."""
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, Date
from models import Expense, Income, Investment
from models.expenses.expense_category_model import ExpensesCategory
from models.incomes.income_category_model import IncomesCategory
from models.investments.investment_category_model import InvestmentsCategory
from models.finance.source_model import Source
from models.users.user_model import User


class SummaryRepository:
    """Repository for fetching aggregated summary data."""

    def __init__(self, db: Session):
        self.db = db

    def get_totals_by_category(
        self,
        start_date: date,
        end_date: date,
        category_type: str = None  # 'expense' | 'income' | 'investment'
    ) -> List[Tuple]:
        """
        Get total amounts aggregated by category.
        
        Returns list of tuples: (category_id, category_name, type, total)
        """
        results = []

        # Expenses aggregation
        if category_type is None or category_type == 'expense':
            expenses = self.db.query(
                Expense.category_id,
                ExpensesCategory.name.label('category_name'),
                func.sum(Expense.amount).label('total')
            ).join(ExpensesCategory).filter(
                and_(
                    Expense.date >= start_date,
                    Expense.date <= end_date,
                    Expense.deleted_at.is_(None)
                )
            ).group_by(Expense.category_id, ExpensesCategory.name).all()
            
            results.extend([
                (cat_id, cat_name, 'expense', float(total))
                for cat_id, cat_name, total in expenses
            ])

        # Incomes aggregation
        if category_type is None or category_type == 'income':
            incomes = self.db.query(
                Income.category_id,
                IncomesCategory.name.label('category_name'),
                func.sum(Income.amount).label('total')
            ).join(IncomesCategory).filter(
                and_(
                    Income.date >= start_date,
                    Income.date <= end_date,
                    Income.deleted_at.is_(None)
                )
            ).group_by(Income.category_id, IncomesCategory.name).all()
            
            results.extend([
                (cat_id, cat_name, 'income', float(total))
                for cat_id, cat_name, total in incomes
            ])

        # Investments aggregation
        if category_type is None or category_type == 'investment':
            investments = self.db.query(
                Investment.category_id,
                InvestmentsCategory.name.label('category_name'),
                func.sum(Investment.amount).label('total')
            ).join(InvestmentsCategory).filter(
                and_(
                    Investment.date >= start_date,
                    Investment.date <= end_date,
                    Investment.deleted_at.is_(None)
                )
            ).group_by(Investment.category_id, InvestmentsCategory.name).all()
            
            results.extend([
                (cat_id, cat_name, 'investment', float(total))
                for cat_id, cat_name, total in investments
            ])

        return results

    def get_totals_over_time(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[date, Dict[str, float]]:
        """
        Get daily totals aggregated by transaction type.
        
        Returns dict: {date: {'expense': total, 'income': total, 'investment': total, 'net': net}}
        """
        daily_totals = {}
        
        # Initialize all dates in range
        current = start_date
        while current <= end_date:
            daily_totals[current] = {'expense': 0.0, 'income': 0.0, 'investment': 0.0}
            current += timedelta(days=1)

        # Expenses by date
        expenses = self.db.query(
            func.cast(Expense.date, Date).label('date'),
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(
                Expense.date >= start_date,
                Expense.date <= end_date,
                Expense.deleted_at.is_(None)
            )
        ).group_by(func.cast(Expense.date, Date)).all()
        
        for exp_date, total in expenses:
            daily_totals[exp_date]['expense'] = float(total)

        # Incomes by date
        incomes = self.db.query(
            func.cast(Income.date, Date).label('date'),
            func.sum(Income.amount).label('total')
        ).filter(
            and_(
                Income.date >= start_date,
                Income.date <= end_date,
                Income.deleted_at.is_(None)
            )
        ).group_by(func.cast(Income.date, Date)).all()
        
        for inc_date, total in incomes:
            daily_totals[inc_date]['income'] = float(total)

        # Investments by date
        investments = self.db.query(
            func.cast(Investment.date, Date).label('date'),
            func.sum(Investment.amount).label('total')
        ).filter(
            and_(
                Investment.date >= start_date,
                Investment.date <= end_date,
                Investment.deleted_at.is_(None)
            )
        ).group_by(func.cast(Investment.date, Date)).all()
        
        for inv_date, total in investments:
            daily_totals[inv_date]['investment'] = float(total)

        # Calculate net
        for date_key in daily_totals:
            daily_totals[date_key]['net'] = (
                daily_totals[date_key]['income'] - daily_totals[date_key]['expense']
            )

        return daily_totals

    def get_income_vs_expense(
        self,
        start_date: date,
        end_date: date
    ) -> Tuple[float, float, int]:
        """
        Get income vs expense totals.
        
        Returns tuple: (total_income, total_expense, transaction_count)
        """
        # Total income
        total_income = self.db.query(
            func.coalesce(func.sum(Income.amount), 0)
        ).filter(
            and_(
                Income.date >= start_date,
                Income.date <= end_date,
                Income.deleted_at.is_(None)
            )
        ).scalar() or 0.0

        # Total expense
        total_expense = self.db.query(
            func.coalesce(func.sum(Expense.amount), 0)
        ).filter(
            and_(
                Expense.date >= start_date,
                Expense.date <= end_date,
                Expense.deleted_at.is_(None)
            )
        ).scalar() or 0.0

        # Transaction count
        expense_count = self.db.query(func.count(Expense.id)).filter(
            and_(
                Expense.date >= start_date,
                Expense.date <= end_date,
                Expense.deleted_at.is_(None)
            )
        ).scalar() or 0

        income_count = self.db.query(func.count(Income.id)).filter(
            and_(
                Income.date >= start_date,
                Income.date <= end_date,
                Income.deleted_at.is_(None)
            )
        ).scalar() or 0

        investment_count = self.db.query(func.count(Investment.id)).filter(
            and_(
                Investment.date >= start_date,
                Investment.date <= end_date,
                Investment.deleted_at.is_(None)
            )
        ).scalar() or 0

        total_count = expense_count + income_count + investment_count

        return float(total_income), float(total_expense), total_count

    def get_totals_by_source(
        self,
        start_date: date,
        end_date: date
    ) -> List[Tuple]:
        """
        Get total amounts aggregated by source for expenses and incomes.

        Returns list of tuples: (source_id, source_name, type, total)
        """
        results = []

        expenses = self.db.query(
            Expense.source_id,
            Source.name.label('source_name'),
            func.sum(Expense.amount).label('total')
        ).join(Source, Expense.source_id == Source.id).filter(
            and_(
                Expense.date >= start_date,
                Expense.date <= end_date,
                Expense.deleted_at.is_(None)
            )
        ).group_by(Expense.source_id, Source.name).all()

        results.extend([
            (src_id, src_name, 'expense', float(total))
            for src_id, src_name, total in expenses
        ])

        incomes = self.db.query(
            Income.source_id,
            Source.name.label('source_name'),
            func.sum(Income.amount).label('total')
        ).join(Source, Income.source_id == Source.id).filter(
            and_(
                Income.date >= start_date,
                Income.date <= end_date,
                Income.deleted_at.is_(None)
            )
        ).group_by(Income.source_id, Source.name).all()

        results.extend([
            (src_id, src_name, 'income', float(total))
            for src_id, src_name, total in incomes
        ])

        return results

    def get_totals_by_user(
        self,
        start_date: date,
        end_date: date
    ) -> List[Tuple]:
        """
        Get total expense amounts aggregated by user.

        Returns list of tuples: (user_id, user_name, total)
        """
        results = self.db.query(
            User.id,
            func.concat(User.name, ' ', User.surname1).label('user_name'),
            func.sum(Expense.amount).label('total')
        ).join(User, Expense.user_id == User.id).filter(
            and_(
                Expense.date >= start_date,
                Expense.date <= end_date,
                Expense.deleted_at.is_(None),
                Expense.user_id.isnot(None)
            )
        ).group_by(User.id, User.name, User.surname1).all()

        return [
            (user_id, user_name, float(total))
            for user_id, user_name, total in results
        ]
