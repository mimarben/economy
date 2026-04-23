import enum


class CurrencyEnum(str, enum.Enum):
    EUR = "EUR"
    USD = "USD"
    JPY = "JPY"
    BTC = "BTC"
    ETH = "ETH"
    USDC = "USDC"
    DOGE = "DOGE",
    LTC = "LTC",
    XRP = "XRP",
    XLM = "XLM",
    ADA = "ADA",
    DOT = "DOT",
    SOL = "SOL",
    SHIB = "SHIB",
    TRX = "TRX"


class RoleEnum(str, enum.Enum):
    HUSBAND = "husband"
    WIFE = "wife"
    CHILD = "child"
    OTHER = "other"


class SourceTypeEnum(str, enum.Enum):
    INCOME = "income"
    SAVING = "saving"
    INVESTMENT = "investment"
    EXPENSE = "expense"
    OTHER = "other"


class ActionEnum(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    HOLD = "hold"


class UserRoleEnum(str, enum.Enum):
    ADMIN = "administrator"
    EDITOR = "editor"
    USER = "user"
    GUEST = "guest"


class TransactionEnum(str, enum.Enum):
    """Types of transactions for categorization rules."""
    EXPENSE = "expense"
    INCOME = "income"
    INVESTMENT = "investment"

class CardTypeEnum(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    REVOLVING = "revolving"