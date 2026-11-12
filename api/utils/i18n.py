import gettext
from io import BytesIO
from contextvars import ContextVar, Token
from pathlib import Path

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po


_locale = ContextVar("locale", default="en")
_catalog_directory = Path(__file__).resolve().parents[1] / "i18n"


class LocalizedMessage(str):
    key: str

    def __new__(cls, value: str, key: str):
        message = super().__new__(cls, value)
        message.key = key
        return message


def _load_translation(language: str) -> tuple[gettext.GNUTranslations, frozenset[str]]:
    catalog_path = _catalog_directory / language / "LC_MESSAGES" / "messages.po"
    with catalog_path.open("rb") as catalog_file:
        catalog = read_po(catalog_file, locale=language)

    compiled_catalog = BytesIO()
    write_mo(compiled_catalog, catalog)
    compiled_catalog.seek(0)
    message_keys = frozenset(
        message.id for message in catalog if isinstance(message.id, str) and message.id
    )
    return gettext.GNUTranslations(compiled_catalog), message_keys


_loaded_catalogs = {language: _load_translation(language) for language in ("en", "es")}
_translations = {language: catalog[0] for language, catalog in _loaded_catalogs.items()}
_message_keys = frozenset().union(*(catalog[1] for catalog in _loaded_catalogs.values()))


def set_locale(language: str) -> Token:
    return _locale.set(language if language in _translations else "en")


def reset_locale(token: Token) -> None:
    _locale.reset(token)


def _(message: str, **kwargs) -> str:
    translated = _translations[_locale.get()].gettext(message)
    if translated == message:
        translated = _translations[_locale.get()].gettext("UNEXPECTED_ERROR")
    if kwargs:
        translated %= kwargs
    return LocalizedMessage(translated, message)


def is_message_key(message: str) -> bool:
    return message in _message_keys
