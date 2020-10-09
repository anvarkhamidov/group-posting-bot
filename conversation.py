import logging

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

import db
from config import restricted

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


@restricted
def add_description(update: Update, context: CallbackContext):
    if 'media_group_id' not in context.chat_data:  # init default data for media_group_id
        context.chat_data['media_group_id'] = 0
    if 'ready_to_send' not in context.chat_data:
        context.chat_data['ready_to_send'] = False
    if 'media' not in context.chat_data:
        context.chat_data['media'] = list()
    message = update.effective_message
    chat_id = update.effective_chat.id
    caption = db.session.query(db.Description).first() or None
    if message.photo:
        context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        # if message.media_group_id:
        #     if message.media_group_id == context.chat_data['media_group_id']:
        #         context.chat_data['media'].append(InputMediaPhoto(media=message.photo[-1].file_id,
        #                                                           caption=caption.text,
        #                                                           parse_mode=ParseMode.HTML))
        #     else:
        #         if context.chat_data['media_group_id'] != 0:
        #             context.chat_data['ready_to_send'] = True
        #         else:
        #             context.chat_data['media'].append(InputMediaPhoto(media=message.photo[-1].file_id,
        #                                                               caption=caption.text,
        #                                                               parse_mode=ParseMode.HTML))
        #         context.chat_data['media_group_id'] = message.media_group_id
        #
        #     print(context.chat_data['media'])
        #
        #     if context.chat_data['ready_to_send']:
        #         context.bot.send_media_group(chat_id=chat_id, media=context.chat_data['media'])
        #         del context.chat_data['media']
        # else:
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

    elif message.document:
        context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        context.bot.send_document(chat_id=chat_id,
                                  document=message.document.file_id,
                                  caption=caption.text,
                                  parse_mode=ParseMode.HTML)
    else:
        return


@restricted
def process_album(update: Update, context: CallbackContext):
    pass
