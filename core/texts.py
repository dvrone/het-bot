import json
from typing import Dict, List

from core.config import BASE_DIR

with open(BASE_DIR / "texts.json", encoding="utf-8") as _f:
    TEXTS: Dict[str, Dict[str, str]] = json.load(_f)

with open(BASE_DIR / "districts.json", encoding="utf-8") as _f:
    KAA_DISTRICTS: Dict[str, Dict[str, list]] = json.load(_f)

with open(BASE_DIR / "request_types.json", encoding="utf-8") as _f:
    REQUEST_TYPES: list = json.load(_f)


def t(lang: str, key: str, **kwargs) -> str:
    """Get translated string, falling back to 'uz' if key missing."""
    text = TEXTS.get(lang, TEXTS["uz"]).get(key) or TEXTS["uz"].get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
