import logging
from functools import wraps

from telegram import Update
from telegram.error import Unauthorized, TimedOut, NetworkError, ChatMigrated, TelegramError, BadRequest
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, \
    CallbackContext, BaseFilter

import db
from config import Config
from conversation import add_description, process_album

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ADMINS = [511773656, 819149807]


class AlbumFilter(BaseFilter):
    def filter(self, message):
        return (message.photo or message.video) and message.media_group_id


album_filter = AlbumFilter()


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMINS:
            logger.warning("Unauthorized access denied for [{}] {}.".format(user_id, update.effective_user.first_name))
            return
        return func(update, context, *args, **kwargs)
    return wrapped


@restricted
def get_description(update: Update, context: CallbackContext):
    description = db.session.query(db.Description).first()

    if not description:
        description = db.Description(text=update.effective_message.text)
        db.session.add(description)
    else:
        if update.message.text == '/start':
            return update.message.reply_text(f'Current text: \n{description.text or "empty"}')
        description.text = update.effective_message.text
    db.session.commit()
    update.message.reply_text('Текст изменён.')


def error_callback(update: Update, context: CallbackContext):
    try:
        logger.warning('Update caused error "%s"', context.error)
#         raise context.error
    except Unauthorized:
        logger.warning('Unauthorized error "%s"', context.error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        logger.warning('BadRequest error "%s"', context.error)
        # handle malformed requests - read more below!
    except TimedOut:
        logger.warning('TimedOut error "%s"', context.error)
        # handle slow connection problems
    except NetworkError:
        logger.warning('NetworkError error "%s"', context.error)
        # handle other connection problems
    except ChatMigrated as e:
        logger.warning('ChatMigrated error "%s"', e)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        logger.warning('TelegramError error "%s"', context.error)
        # handle all other telegram related errors


def main():
    updater = Updater(token=Config.get('token'), use_context=True)
    private = MessageHandler(Filters.private & Filters.text, get_description)
    group = MessageHandler(Filters.group & (Filters.document | Filters.photo | Filters.video | Filters.animation), add_description)
    updater.dispatcher.add_handler(MessageHandler(album_filter, process_album))
    updater.dispatcher.add_handler(private)
    updater.dispatcher.add_handler(group)
    updater.dispatcher.add_error_handler(error_callback)
    return updater


if __name__ == '__main__':
    Config.validate()
    upd = main()
    print('Bot started')
    upd.start_polling()
    upd.idle()
