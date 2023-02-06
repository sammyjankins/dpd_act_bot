import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

from telegram import __version__ as TG_VER
from telegram.constants import ParseMode

import sort_by_date_created

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Make a folder and save the photo."""

    if not os.path.exists('photo'):
        os.makedirs('photo')
    file = await update.channel_post.photo[-1].get_file()
    await file.download_to_drive(custom_path=f'photo/{file.file_unique_id}.jpg')
    await update.effective_chat.send_message(f"Файл {file.file_unique_id}.jpg сохранен.")


async def send_photos(context: CallbackContext):
    """Check if the folder exists and send photo."""

    if not os.path.exists('photo'):
        await context.bot.send_message(chat_id=context.job.chat_id, text='Нет фото для отправки.')
    else:
        sort_by_date_created.sort_to_dirs('photo')
        sort_by_date_created.archive('photo', 'photo')
        sort_by_date_created.send('photo.zip', secrets.EMAIL_TO, secrets.EMAIL_SUBJECT)
        await context.bot.send_message(chat_id=context.job.chat_id,
                                       text=f'Фото отправлены на адрес {secrets.EMAIL_TO}.')


async def task_enabler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Setting a task from the data in the message text."""

    if 'send' in update.channel_post.text:
        j = context.job_queue

        # eval first execution point
        datetime_str = update.channel_post.text.replace('send ', '')  # example: 03.02.23 03:00
        datetime_start = datetime.strptime(datetime_str, '%d.%m.%y %H:%M')
        local_timezone = datetime.now(timezone.utc).astimezone().tzinfo
        datetime_start = datetime_start.replace(tzinfo=local_timezone)

        j.run_repeating(send_photos, timedelta(days=3), first=datetime_start, chat_id=update.effective_chat.id)

        await update.effective_chat.send_message(
            f'Задача будет запущена в {datetime_start}',
            parse_mode=ParseMode.HTML,
        )


def main() -> None:
    """Start the bot."""

    application = Application.builder().token(secrets.TG_TOKEN).build()

    application.add_handler(MessageHandler(filters.PHOTO, photo))
    application.add_handler(MessageHandler(filters.TEXT, task_enabler))

    application.run_polling()


if __name__ == "__main__":
    main()
