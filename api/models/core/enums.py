import enum


class CurrencyEnum(str, enum.Enum):
    euro = "€"
    dolar = "$"
    yuan = "¥"
    bitcoin = "₿"
    ethereum = "Ξ"
    usdc = "USDC"
    dogecoin = "DOGE"
    litecoin = "LTC"
    ripple = "XRP"
    stellar = "XLM"
    cardano = "ADA"
    polkadot = "DOT"
    solana = "SOL"
    shiba_inu = "SHIB"
    tron = "TRX"


class RoleEnum(str, enum.Enum):
    husband = "husband"
    wife = "wife"
    child = "child"
    other = "other"


class SourceTypeEnum(str, enum.Enum):
    income = "income"
    saving = "saving"
    investment = "investment"
    expense = "expense"
    other = "other"


class ActionEnum(str, enum.Enum):
    buy = "buy"
    sell = "sell"
    transfer = "transfer"
    deposit = "deposit"
    withdraw = "withdraw"
    hold = "hold"


class UserRoleEnum(str, enum.Enum):
    ADMIN = "administrator"
    EDITOR = "editor"
    USER = "user"
    GUEST = "guest"
