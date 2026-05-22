from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.texts import KAA_DISTRICTS, REQUEST_TYPES, t


def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
            [InlineKeyboardButton(text="Qaraqalpaqsha", callback_data="lang:kaa")],
        ]
    )


def type_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "btn_individual"), callback_data="type:individual"
                ),
                InlineKeyboardButton(
                    text=t(lang, "btn_legal"), callback_data="type:legal"
                ),
            ]
        ]
    )


def regions_keyboard(lang: str) -> InlineKeyboardMarkup:
    names = {
        "uz": "Qoraqalpogʻiston Respublikasi",
        "ru": "Республика Каракалпакстан",
        "kaa": "Qaraqalpaqstan Respublikası",
    }
    name = names.get(lang, names["uz"])
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"region:{name}")]
        ]
    )


def districts_keyboard(lang: str) -> InlineKeyboardMarkup:
    districts = list(KAA_DISTRICTS.get(lang, KAA_DISTRICTS["uz"]).keys())
    rows = []
    for i in range(0, len(districts), 2):
        row = [
            InlineKeyboardButton(
                text=districts[i], callback_data=f"district:{districts[i]}"
            )
        ]
        if i + 1 < len(districts):
            row.append(
                InlineKeyboardButton(
                    text=districts[i + 1], callback_data=f"district:{districts[i + 1]}"
                )
            )
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def reply_keyboard(request_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "btn_reply"), callback_data=f"reply:{request_id}"
                )
            ]
        ]
    )


def profile_keyboard(lang: str) -> InlineKeyboardMarkup:
    fields = [
        ("✏️ " + t(lang, "edit_name"), "edit:name"),
        ("📞 " + t(lang, "edit_phone"), "edit:phone"),
        ("📍 " + t(lang, "edit_region"), "edit:region"),
        ("🏘 " + t(lang, "edit_district"), "edit:district"),
        ("🏠 " + t(lang, "edit_address"), "edit:address"),
        ("🔢 " + t(lang, "edit_account_number"), "edit:account_number"),
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=cd)] for text, cd in fields
        ]
    )


def request_categories_keyboard(lang: str) -> InlineKeyboardMarkup:
    categories = REQUEST_TYPES.get(lang, REQUEST_TYPES["uz"])
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat["label"], callback_data=f"cat:{cat['id']}")]
            for cat in categories
        ]
    )


def request_types_keyboard(lang: str, category_id: str) -> InlineKeyboardMarkup:
    categories = REQUEST_TYPES.get(lang, REQUEST_TYPES["uz"])
    category = next((c for c in categories if c["id"] == category_id), None)
    if not category:
        return InlineKeyboardMarkup(inline_keyboard=[])
    rows = [
        [InlineKeyboardButton(text=tp["label"], callback_data=f"rtype:{tp['id']}")]
        for tp in category["types"]
    ]
    rows.append(
        [
            InlineKeyboardButton(
                text="⬅️ " + t(lang, "btn_back"), callback_data="cat:back"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def requests_filter_keyboard(
    current: str, page: int, total_pages: int
) -> InlineKeyboardMarkup:
    filters = [
        ("🕐 Kutilmoqda", "pending"),
        ("✅ Javob berilgan", "replied"),
        ("📋 Hammasi", "all"),
    ]
    filter_row = [
        InlineKeyboardButton(
            text=("▸ " if current == f else "") + label,
            callback_data=f"rfilter:{f}:0",
        )
        for label, f in filters
    ]
    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️", callback_data=f"rfilter:{current}:{page - 1}"
            )
        )
    nav_row.append(
        InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop")
    )
    if page + 1 < total_pages:
        nav_row.append(
            InlineKeyboardButton(
                text="➡️", callback_data=f"rfilter:{current}:{page + 1}"
            )
        )

    rows = [filter_row]
    if total_pages > 1:
        rows.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=rows)
