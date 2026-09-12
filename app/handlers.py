from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    PreCheckoutQuery,
)

router = Router()

prices = {
    "full": [
        ("По плечи", 60),
        ("По пояс", 80),
        ("Фулл", 100),
    ],
    "half": [
        ("По плечи", 40),
        ("По пояс", 60),
        ("Фулл", 80),
    ],
    "sketch": [
        ("По плечи", 25),
        ("По пояс", 40),
        ("Фулл", 60),
    ],
}

names = {
    "full": "✨ Полный рендер",
    "half": "🌙 Халф рендер",
    "sketch": "✏️ Скетч",
}


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=names["full"],
                    callback_data="type:full"
                )
            ],
            [
                InlineKeyboardButton(
                    text=names["half"],
                    callback_data="type:half"
                )
            ],
            [
                InlineKeyboardButton(
                    text=names["sketch"],
                    callback_data="type:sketch"
                )
            ],
        ]
    )


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎨 <b>КОМИШЕНЫ</b>\n\n"
        "Выберите тип работы:",
        reply_markup=main_menu()
    )


@router.callback_query(F.data.startswith("type:"))
async def choose_type(callback: CallbackQuery):
    work_type = callback.data.split(":")[1]

    buttons = []

    for size, price in prices[work_type]:
        buttons.append([
            InlineKeyboardButton(
                text=f"{size} — {price} ⭐",
                callback_data=f"pay:{work_type}:{price}"
            )
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        f"<b>{names[work_type]}</b>\n\n"
        "Выберите размер:",
        reply_markup=keyboard
    )

    await callback.answer()


@router.callback_query(F.data.startswith("pay:"))
async def pay(callback: CallbackQuery, bot):
    _, work_type, price = callback.data.split(":")
    price = int(price)

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=names[work_type],
        description="Комиссия за арт 🎨",
        payload=f"commission:{work_type}:{price}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Комиссия",
                amount=price
            )
        ],
    )

    await callback.answer()


@router.pre_checkout_query()
async def checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def payment_success(message: Message):
    await message.answer(
        "✅ <b>Оплата прошла успешно!</b>\n\n"
        "Спасибо за заказ! 💗"
)
