import sys
from typing import Type, Optional
import json
import hashlib
import subprocess
from pathlib import Path
from pydantic import BaseModel
import re

# ─────────────────────────────────────────────
# Path setup — permite importar desde api/
# ─────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

# ─────────────────────────────────────────────
# Patches: reemplaza enums inline por imports Angular
# ─────────────────────────────────────────────
ENUM_PATCHES: dict[str, str] = {
    'export type CurrencyEnum = "EURO" | "USD" | "JPY" | "BTC" | "ETH" | "USDC" | "DOGE" | "LTC" | "XRP" | "XLM" | "ADA" | "DOT" | "SOL" | "SHIB" | "TRX";':
        'import { CurrencyEnum } from "@core/const/Currency.enum";',
    'export type RoleEnum = "husband" | "wife" | "child" | "other";':
        'import { RoleEnum } from "@core/const/Role.enum";',

    'export type SourceTypeEnum = "INCOME" | "SAVING" | "INVESTMENT" | "EXPENSE" | "OTHER";':
        'import { SourceTypeEnum } from "@core/const/SourceType.enum";',

    'export type ActionEnum = "BUY" | "SELL" | "TRANSFER" | "DEPOSIT" | "WITHDRAW" | "HOLD";':
        'import { ActionEnum } from "@core/const/Action.enum";',

    'export type UserRoleEnum = "ADMINISTRATOR" | "EDITOR" | "USER" | "GUEST";':
        'import { UserRoleEnum } from "@core/const/UserRole.enum";',

    'export type TransactionEnum = "EXPENSE" | "INCOME" | "INVESTMENT";':
        'import { TransactionEnum } from "@core/const/Transaction.enum";',
}


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def apply_patches(content: str, ts_patches: dict[str, str]) -> str:
    """Aplica reemplazos exactos con fallback regex por nombre de tipo."""
    for old, new in ts_patches.items():
        type_name = old.split("=")[0].replace("export type", "").strip()
        if old in content:
            content = content.replace(old, new)
            print(f"  ✔ Patch exacto:  {type_name}")
        else:
            pattern = rf'export type {type_name} = [^;]+;'
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, new, content, flags=re.DOTALL)
                print(f"  ✔ Patch regex:   {type_name}")
            else:
                print(f"  ⏭ No presente:   {type_name}")
    return content


# ─────────────────────────────────────────────
# Core
# ─────────────────────────────────────────────
def schema_exporter(
    model: Type[BaseModel],
    generate_ts: bool = True,
    ts_patches: Optional[dict[str, str]] = None
) -> bool:
    """
    Exporta esquema JSON y genera TypeScript.
    Retorna True si hubo cambios, False si estaba actualizado.
    """
    schema = model.model_json_schema()
    schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
    current_hash = hashlib.md5(schema_json.encode()).hexdigest()

    output_dir = Path(__file__).parent / 'client' / 'schemas'
    ts_output_dir = Path(__file__).parent / 'client' / 'models'
    output_dir.mkdir(parents=True, exist_ok=True)
    ts_output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"{model.__name__}_schema.json"
    hash_path = output_dir / f"{model.__name__}.hash"
    ts_path   = ts_output_dir / f"{model.__name__}.ts"

    if hash_path.exists() and hash_path.read_text() == current_hash:
        print(f"⏭ Sin cambios: {model.__name__}")
        return False

    json_path.write_text(schema_json, encoding="utf-8")
    hash_path.write_text(current_hash)
    print(f"✔ Schema actualizado: {model.__name__}")

    if generate_ts:
        result = subprocess.run(
            ["json2ts", "-i", str(json_path), "-o", str(ts_path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"❌ Error json2ts ({model.__name__}):", result.stderr)
            return True

        if ts_patches:
            content = ts_path.read_text(encoding="utf-8")
            content = apply_patches(content, ts_patches)  # ✅ ahora sí se usa
            ts_path.write_text(content, encoding="utf-8")

        print(f"✔ TypeScript generado: {ts_path}")

    return True


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
if __name__ == "__main__":
    from schemas.finance.source_schema import SourceRead
    from schemas.cards.card_schema import CardRead
    from schemas.imports.import_origin_schema import ImportOriginRead
    from schemas.imports.import_profile_schema import ImportProfileCreate
    from schemas.users.user_schema import UserRead, UserCreate
    from schemas.finance.account_schema import AccountCreate
    #from schemas.expenses.expense_schema import ExpenseRead
    #from schemas.expenses.expense_category_schema import ExpenseCategoryRead
    #from schemas.incomes.income_schema import IncomeRead
    #from schemas.incomes.income_category_schema import IncomeCategoryRead

    models = [
        SourceRead,
        CardRead,
        ImportOriginRead,
        ImportProfileCreate,
        UserRead,
        UserCreate,
        AccountCreate,
        #AccountRead,  # Skip because of forward references to UserRead
        #BankRead,
        #ExpenseRead,
        #ExpenseCategoryRead,
        #IncomeRead,
        #IncomeCategoryRead,
    ]

    changed = [m.__name__ for m in models if schema_exporter(m, ts_patches=ENUM_PATCHES)]

    print("\n─────────────────────────────")
    if changed:
        print(f"🔄 Regenerados: {', '.join(changed)}")
    else:
        print("✅ Todo sincronizado, sin cambios.")