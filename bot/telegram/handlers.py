from asgiref.sync import sync_to_async
from django.conf import settings
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler

from bot.models import User, Task, Location, Hint
import os


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_telegram_id = update.effective_user.id
    username = update.effective_user.username

    # Получение или создание пользователя
    user, created = await sync_to_async(User.objects.get_or_create)(
        telegram_id=user_telegram_id,
        defaults={'username': username, 'coins': 0}
    )

    # Обнуление баланса монет
    if not created:  # Если пользователь уже существовал
        user.coins = 0
        await sync_to_async(user.save)()

    # Получение первой локации
    first_location = await sync_to_async(Location.objects.order_by('order').first)()
    if first_location:
        response = (
            f"👋 *Привет, {user.username or 'Игрок'}! Добро пожаловать в квест!* 🗺️\n\n"
            f"📜 *Описание*: _{first_location.description}_\n"
            f"💰 *Награда за прохождение*: `{first_location.hint_cost}` монет 🪙"
        )

        # Кнопка для начала приключения
        keyboard = [
            [InlineKeyboardButton("🚀 Начать приключение", callback_data=f"start_location_{first_location.id}")],
            [InlineKeyboardButton("Баланс 🪙", callback_data="show_balance")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("⚠️ *Квест не настроен. Обратитесь позже.*", parse_mode=ParseMode.MARKDOWN)


async def start_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Извлечение id локации из callback_data
    location_id = int(query.data.split("_")[-1])
    location = await sync_to_async(Location.objects.get)(id=location_id)
    user_telegram_id = query.from_user.id
    user = await sync_to_async(User.objects.get)(telegram_id=user_telegram_id)

    # Получение первой задачи из локации
    task = await sync_to_async(location.tasks.order_by('order').first)()
    if task:
        # Сохраняем ID текущей задачи в контексте пользователя
        context.user_data['current_task_id'] = task.id

        response = f"Угадай название первой локации по картинке"

        # Кнопка для подсказки
        keyboard = [
            [InlineKeyboardButton("Подсказка", callback_data=f"hint_{task.id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправка изображения, если оно есть
        if task.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(task.image))
            if os.path.exists(image_path):
                with open(image_path, 'rb') as image_file:
                    await context.bot.send_photo(chat_id=query.message.chat_id, photo=image_file)

        await query.message.reply_text(response, reply_markup=reply_markup)
    else:
        await query.message.reply_text("Нет задач в этой локации.")


async def hint_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Извлечение id задачи из callback_data
    task_id = int(query.data.split("_")[-1])
    task = await sync_to_async(Task.objects.get)(id=task_id)
    user_telegram_id = query.from_user.id
    user = await sync_to_async(User.objects.get)(telegram_id=user_telegram_id)

    # Проверка, достаточно ли монет для подсказки
    hint_cost = await sync_to_async(lambda: task.location.hint_cost)()
    if user.coins >= hint_cost:
        user.coins -= hint_cost
        await sync_to_async(user.save)()

        response = f"Подсказка для задачи: {task.text}\n\n"
        response += f"{task.answer[:3]}... (конец подсказки)"
        await query.message.reply_text(response)
    else:
        await query.message.reply_text("Недостаточно монет для подсказки!")


async def process_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_telegram_id = update.effective_user.id
    user = await sync_to_async(User.objects.get)(telegram_id=user_telegram_id)

    # Получение текущей задачи из контекста
    task_id = context.user_data.get('current_task_id')
    if not task_id:
        await update.message.reply_text("У вас нет активной задачи.")
        return

    task = await sync_to_async(Task.objects.get)(id=task_id)
    user_answer = update.message.text.strip().lower()  # Приводим ответ пользователя к нижнему регистру
    correct_answer = task.answer.lower()  # Приводим правильный ответ к нижнему регистру

    # Проверяем совпадение ключевой части ответа
    if correct_answer in user_answer or user_answer in correct_answer:
        # Увеличиваем баланс монет
        user.coins += task.reward
        await sync_to_async(user.save)()

        response = (
            f"✅ *Правильно!* Вы получили `{task.reward}` монет 🪙\n"
            f"💎 *Ваш баланс*: `{user.coins}` монет 🪙"
        )

        # Переход к следующей задаче
        next_task = await sync_to_async(
            lambda: Task.objects.filter(location=task.location, order__gt=task.order).order_by('order').first()
        )()

        if next_task:
            context.user_data['current_task_id'] = next_task.id
            response += f"\n\n🔍 *Следующая задача*: _{next_task.text}_"

            # Отправка сообщения с текстом задачи
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

            # Отправка изображения задачи, если оно есть
            if next_task.image:
                image_path = os.path.join(settings.MEDIA_ROOT, str(next_task.image))
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as image_file:
                        await context.bot.send_photo(chat_id=update.message.chat_id, photo=image_file)

            # Кнопка для подсказки
            keyboard = [
                [InlineKeyboardButton("💡 Подсказка", callback_data=f"hint_{next_task.id}")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Отправка кнопок
            await update.message.reply_text("", reply_markup=reply_markup)
        else:
            # Завершение локации
            del context.user_data['current_task_id']  # Удаляем текущую задачу из контекста
            response += "\n\n🏁 *Вы завершили все задачи в этой локации!*"
            keyboard = [
                [InlineKeyboardButton("🚩 Я на месте", callback_data=f"finish_location_{task.location.id}")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(response, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        # Неправильный ответ
        response = "❌ *Неправильно.* Попробуйте ещё раз."
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_telegram_id = query.from_user.id
    user = await sync_to_async(User.objects.get)(telegram_id=user_telegram_id)

    response = f"Ваш текущий баланс: {user.coins} монет."
    await query.message.reply_text(response)


async def hint_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Извлечение ID задачи и подсказки из callback_data
    data = query.data.split("_")
    task_id = int(data[1])
    hint_id = int(data[2]) if len(data) > 2 else None

    task = await sync_to_async(Task.objects.get)(id=task_id)
    user_telegram_id = query.from_user.id
    user = await sync_to_async(User.objects.get)(telegram_id=user_telegram_id)

    if hint_id:
        # Получение конкретной подсказки
        hint = await sync_to_async(Hint.objects.get)(id=hint_id)
        if user.coins >= hint.cost:
            user.coins -= hint.cost
            await sync_to_async(user.save)()

            response = f"Подсказка для задачи: {task.text}\n\n"
            response += f"{hint.text}"
            if hint.image:
                image_path = os.path.join(settings.MEDIA_ROOT, str(hint.image))
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as image_file:
                        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_file)
            await query.message.reply_text(response)
        else:
            await query.message.reply_text("Недостаточно монет для подсказки!")
    else:
        # Отправка списка подсказок
        hints = await sync_to_async(lambda: list(task.hints.all()))()
        if hints:
            keyboard = [
                [InlineKeyboardButton(f"Подсказка {hint.order + 1} (Стоимость: {hint.cost} монет)", callback_data=f"hint_{task_id}_{hint.id}")]
                for hint in hints
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Выберите подсказку:", reply_markup=reply_markup)
        else:
            await query.message.reply_text("Для этой задачи нет подсказок.")


async def finish_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Извлечение id локации из callback_data
    location_id = int(query.data.split("_")[-1])
    location = await sync_to_async(Location.objects.get)(id=location_id)
    user_telegram_id = query.from_user.id
    user = await sync_to_async(User.objects.get)(telegram_id=user_telegram_id)

    # Начисление монет за завершение локации
    user.coins += location.hint_cost
    await sync_to_async(user.save)()

    # Получение следующей локации
    next_location = await sync_to_async(
        lambda: Location.objects.filter(order__gt=location.order).order_by('order').first()
    )()

    if next_location:
        response = (
            f"🎉 *Вы успешно завершили локацию*: _{location.name}_! 🏁\n\n"
            f"💰 *Награда*: `{location.hint_cost}` монет 🪙\n"
            f"💎 *Ваш текущий баланс*: `{user.coins}` монет 🪙\n\n"
            f"📖 *_{next_location.description}_"
        )

        # Кнопка для начала следующей локации
        keyboard = [
            [InlineKeyboardButton("➡️ Перейти к следующей локации", callback_data=f"start_location_{next_location.id}")],
            [InlineKeyboardButton("Баланс 🪙", callback_data="show_balance")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(response, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        response = (
            f"🎉 *Вы успешно завершили локацию*: _{location.name}_! 🏁\n\n"
            f"💰 *Награда*: `{location.hint_cost}` монет 🪙\n"
            f"💎 *Ваш текущий баланс*: `{user.coins}` монет 🪙\n\n"
            f"🎊 *Поздравляем, вы завершили весь квест!* 🏆"
        )
        await query.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)