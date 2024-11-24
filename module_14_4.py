from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import initiate_db, get_all_products
import asyncio

initiate_db()

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# Основное меню
main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_keyboard.add(KeyboardButton("Рассчитать"), KeyboardButton("Информация"), KeyboardButton("Купить"))

# Inline-меню для покупки
inline_buy_menu = InlineKeyboardMarkup(resize_keyboard=True)
inline_buy_menu.add(
    InlineKeyboardButton("Product1", callback_data="product_buying"),
    InlineKeyboardButton("Product2", callback_data="product_buying"),
    InlineKeyboardButton("Product3", callback_data="product_buying"),
    InlineKeyboardButton("Product4", callback_data="product_buying")
)

# Inline-меню для других опций
inline_menu_kb = InlineKeyboardMarkup(resize_keyboard=True)
inline_menu_kb.add(InlineKeyboardButton("Рассчитать норму калорий", callback_data="calories"),
                   InlineKeyboardButton("Формулы расчёта", callback_data="formulas"))


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


# Хэндлеры для основного меню
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я бот для расчёта калорий и покупки продуктов. Выберите опцию ниже:", reply_markup=main_menu_keyboard)


@dp.message_handler(lambda message: message.text.lower() == "рассчитать")
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=inline_menu_kb)


@dp.message_handler(lambda message: message.text.lower() == "купить")
async def get_buying_list(message: types.Message):
    products = get_all_products()  # Получаем данные из таблицы Products

    if not products:
        await message.answer("Продукты временно отсутствуют.")
        return

    # Связь между продуктами и их изображениями (если путь к изображениям не хранится в БД)
    product_images = {
        "Product1": "images/product1.jpg",
        "Product2": "images/product2.jpg",
        "Product3": "images/product3.jpg",
        "Product4": "images/product4.jpg"
    }

    for product in products:
        product_id, title, description, price, image_path = product
        image_path = product_images.get(title, None)  # Получаем путь к изображению по названию продукта

        if image_path:  # Если изображение найдено
            try:
                with open(image_path, "rb") as photo:
                    await message.answer_photo(
                        photo=photo,
                        caption=f"Название: {title} | Описание: {description} | Цена: {price}₽"
                    )
            except FileNotFoundError:
                await message.answer(
                    f"Название: {title} | Описание: {description} | Цена: {price}₽\n⚠️ Изображение не найдено."
                )
        else:  # Если изображения нет в словаре
            await message.answer(
                f"Название: {title} | Описание: {description} | Цена: {price}₽\n⚠️ Изображение отсутствует."
            )

    await message.answer("Выберите продукт для покупки:", reply_markup=inline_buy_menu)


@dp.callback_query_handler(lambda call: call.data == "product_buying")
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


# Хэндлеры для расчёта калорий
@dp.callback_query_handler(lambda call: call.data == "formulas")
async def get_formulas(call: types.CallbackQuery):
    formula = (
        "Формула Миффлина-Сан Жеора (для мужчин):\n"
        "BMR = 10 × вес (кг) + 6.25 × рост (см) − 5 × возраст (лет) + 5\n\n"
        "Формула Миффлина-Сан Жеора (для женщин):\n"
        "BMR = 10 × вес (кг) + 6.25 × рост (см) − 5 × возраст (лет) − 161"
    )
    await call.message.answer(formula)
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == "calories")
async def set_age(call: types.CallbackQuery):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    # Преобразование данных в нужные типы
    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))

    # Формула Миффлина - Сан Жеора (для мужчин)
    bmr1 = 10 * weight + 6.25 * growth - 5 * age + 5
    # Формула Миффлина - Сан Жеора (для женщин)
    bmr2 = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.answer(f"Ваша норма калорий: {bmr1} ккалорий для мужчин.")
    await message.answer(f"Ваша норма калорий: {bmr2} ккалорий для женщин.")
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
