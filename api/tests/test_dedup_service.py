from services.core.dedup_service import generate_dedup_hash


def test_generate_dedup_hash_normalization_equivalence():
    hash1 = generate_dedup_hash(
        account_id=123,
        txn_date='2026-03-30',
        amount='100.0',
        description='  Compra  cafés ')

    hash2 = generate_dedup_hash(
        account_id=123,
        txn_date='2026-03-30',
        amount='100.000',
        description='compra cafés')

    assert hash1 == hash2


def test_generate_dedup_hash_different_account_unequal():
    hash1 = generate_dedup_hash(100, '2026-03-30', 50.50, 'gasto')
    hash2 = generate_dedup_hash(101, '2026-03-30', 50.50, 'gasto')

    assert hash1 != hash2


def test_duplicate_detection_via_set():
    items = [
        (1, '2026-03-30', 10.0, 'Test'),
        (1, '2026-03-30', 10.00, 'test '),
        (1, '2026-03-30', 11.0, 'Test'),
    ]

    seen = set()
    duplicates = 0
    for account, date, amount, desc in items:
        h = generate_dedup_hash(account, date, amount, desc)
        if h in seen:
            duplicates += 1
        else:
            seen.add(h)

    assert duplicates == 1
    assert len(seen) == 2
