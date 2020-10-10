import logging

from telegram import Update
from telegram.error import Unauthorized, TimedOut, NetworkError, ChatMigrated, TelegramError, BadRequest
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, BaseFilter
from telegram.utils.request import Request

import db
from config import Config, restricted
import mqbot
from conversation import add_description, process_album

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class AlbumFilter(BaseFilter):
    def filter(self, message):
        return (message.photo or message.video) and message.media_group_id


album_filter = AlbumFilter()


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
    queue = mqbot.mq.MessageQueue(all_burst_limit=20, all_time_limit_ms=1017, group_burst_limit=20, group_time_limit_ms=60000)
    bot = mqbot.MQBot(token=Config.get('token'), request=Request(con_pool_size=8), mqueue=queue)
    updater = Updater(bot=bot, use_context=True)
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
