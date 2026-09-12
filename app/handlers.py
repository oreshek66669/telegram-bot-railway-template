"""Update handlers. Add your own commands here — see README "Extending the bot".

The ``db: Storage`` argument is injected by aiogram's dependency injection:
``main.py`` puts the storage into the dispatcher's workflow data under the
key ``db``, and any handler that declares a parameter with that name gets it.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from db import Storage

router = Router(name="commissions")


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✨ Полный рендер",
                    callback_data="type:full",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌙 Халф рендер",
                    callback_data="type:half",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Скетч",
                    callback_data="type:sketch",
                )
            ],
        ]
    )


def size_menu(render_type: str) -> InlineKeyboardMarkup:
    prices = {
        "full": {
            "shoulders": 60,
            "waist": 80,
            "fullbody": 100,
        },
        "half": {
            "shoulders": 40,
            "waist": 60,
            "fullbody": 80,
        },
        "sketch": {
            "shoulders": 25,
            "waist": 40,
            "fullbody": 60,
        },
    }

    names = {
        "shoulders": "По плечи",
        "waist": "По пояс",
        "fullbody": "Фулл",
    }

    buttons = []

    for size, price in prices[render_type].items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{names[size]} — {price} ⭐",
                callback_data=f"pay:{render_type}:{size}:{price}",
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="back:main",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(CommandStart())
async def cmd_start(message: Message, db: Storage) -> None:
    user = message.from_user

    if user is not None:
        await db.track_user(user.id, user.username)

    await message.answer(
        "🎨 <b>КОМИШЕНЫ</b>\n\n"
        "Выберите тип работы:\n\n"
        "✨ Полный рендер — от 60 ⭐\n"
        "🌙 Халф рендер — от 40 ⭐\n"
        "✏️ Скетч — от 25 ⭐\n\n"
        "Выберите вариант ниже:",
        reply_markup=main_menu(),
    )


@router.callback_query(F.data.startswith("type:"))
async def choose_type(callback: CallbackQuery) -> None:
    render_type = callback.data.split(":")[1]

    names = {
        "full": "✨ Полный рендер",
        "half": "🌙 Халф рендер",
        "sketch": "✏️ Скетч",
    }

    await callback.message.edit_text(
        f"<b>{names[render_type]}</b>\n\n"
        "Выберите размер:",
        reply_markup=size_menu(render_type),
    )

    await callback.answer()


@router.callback_query(F.data == "back:main")
async def back_main(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "🎨 <b>КОМИШЕНЫ</b>\n\n"
        "Выберите тип работы:",
        reply_markup=main_menu(),
    )

    await callback.answer()


@router.callback_query(F.data.startswith("pay:"))
async def create_invoice(callback: CallbackQuery, bot) -> None:
    _, render_type, size, price = callback.data.split(":")
    price = int(price)

    names = {
        "full": "Полный рендер",
        "half": "Халф рендер",
        "sketch": "Скетч",
    }

    sizes = {
        "shoulders": "По плечи",
        "waist": "По пояс",
        "fullbody": "Фулл",
    }

    title = f"{names[render_type]} — {sizes[size]}"

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=title,
        description="Комиссия за арт",
        payload=f"commission:{render_type}:{size}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label=title,
                amount=price,
            )
        ],
    )

    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout(
    pre_checkout_query: PreCheckoutQuery,
) -> None:
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    await message.answer(
        "✅ <b>Оплата прошла успешно!</b>\n\n"
        "Спасибо за заказ! 💗"
    )


@router.message(F.text)
async def text_handler(message: Message) -> None:
    await message.answer(
        "🎨 Чтобы оформить заказ, нажмите /start"
    )
