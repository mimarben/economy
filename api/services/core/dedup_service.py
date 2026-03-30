import hashlib
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime


def _normalize_description(description: str | None) -> str:
    if description is None:
        return ""
    # lowercase, trim, collapse whitespace
    normalized = " ".join(description.strip().lower().split())
    return normalized


def _normalize_date(txn_date: date | datetime | str) -> str:
    if isinstance(txn_date, str):
        txn_date = datetime.fromisoformat(txn_date)
    if isinstance(txn_date, datetime):
        txn_date = txn_date.date()
    if isinstance(txn_date, date):
        return txn_date.strftime("%Y-%m-%d")
    raise ValueError("Invalid date for dedup hash")


def _normalize_amount(amount: float | str | Decimal) -> str:
    amt = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{amt:.2f}"


def generate_dedup_hash(
    account_id: int | None,
    txn_date: date | datetime | str,
    amount: float | str | Decimal,
    description: str | None,
    fuzzy_match: bool = False
) -> str:
    """Generate deterministic per-account dedup fingerprint for transactions."""
    if account_id is None:
        raise ValueError("account_id is required for dedup hash")

    normalized_date = _normalize_date(txn_date)
    normalized_amount = _normalize_amount(amount)
    normalized_description = _normalize_description(description)

    payload = f"{account_id}|{normalized_date}|{normalized_amount}|{normalized_description}"
    # keep to fixed-length hash (64 chars)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
