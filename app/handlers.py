from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, PreCheckoutQuery

router = Router()

prices = {
    "full": [("По плечи", 60), ("По пояс", 80), ("Фулл", 100)],
    "half": [("По плечи", 40), ("По пояс", 60), ("Фулл", 80)],
    "sketch": [("По плечи", 25), ("По пояс", 40), ("Фулл", 60)]
}

names = {
    "full": "✨ Полный рендер",
    "half": "🌙 Халф рендер",
    "sketch": "✏️ Скетч"
}

def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=names[x], callback_data=f"type:{x}")]
        for x in prices
    ])

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎨 <b>КОМИШЕНЫ</b>\n\nВыберите тип работы:",
        reply_markup=menu()
    )

@router.callback_query(F.data.startswith("type:"))
async def choose(callback: CallbackQuery):
    t = callback.data.split(":")[1]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{size} — {price} ⭐",
         callback_data=f"pay:{t}:{price}")]
        for size, price in prices[t]
    ])
    await callback.message.edit_text(
        f"<b>{names[t]}</b>\n\nВыберите размер:",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pay:"))
async def pay(callback: CallbackQuery, bot):
    _, t, price = callback.data.split(":")
    price = int(price)

    await bot.send_invoice(
        callback.from_user.id,
        title=names[t],
        description="Комиссия за арт",
        payload=f"commission:{t}:{price}",
        currency="XTR",
        prices=[LabeledPrice(label="Комиссия", amount=price)]
    )
    await callback.answer()

@router.pre_checkout_query()
async def checkout(q: PreCheckoutQuery):
    await q.answer(ok=True)

@router.message(F.successful_payment)
async def paid(message: Message):
    await message.answer(
        "✅ <b>Оплата прошла успешно!</b>\n\n"
        "Спасибо за заказ! 💗"
    )
