import logging
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ReplyKeyboardRemove
from telegram.ext import CallbackContext, run_async, ConversationHandler

import db
from config import Config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def add_description(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    caption = db.session.query(db.Description).first() or None
    if message.photo:
        context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        context.bot.send_photo(chat_id=chat_id,
                               caption=caption.text,
                               photo=message.photo[-1].file_id,
                               parse_mode=ParseMode.HTML)

    elif message.animation:
        context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        context.bot.send_animation(chat_id=chat_id,
                                   caption=caption.text,
                                   animation=message.animation.file_id,
                                   parse_mode=ParseMode.HTML)
    elif message.video:
        context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        context.bot.send_video(chat_id=chat_id,
                               video=message.video.file_id,
                               caption=caption.text,
                               parse_mode=ParseMode.HTML)
    else:
        return
