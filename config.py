import os
import logging
from functools import wraps

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

ADMINS = [511773656, 819149807, 355518558]


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        if update.effective_chat.type == 'supergroup':
            user_id = update.effective_message.from_user.id
        else:
            user_id = update.effective_message.id
        if user_id not in ADMINS:
            logger.warning("Unauthorized access denied for [{}] {}.".format(user_id, update.effective_user.first_name))
            return
        return func(update, context, *args, **kwargs)
    return wrapped


class Config:
    __config = {
        'token': str(os.getenv('TOKEN')),
        'group_id': str(os.getenv('GROUP_ID')),
    }

    @staticmethod
    def get(key):
        try:
            return Config.__config[key]
        except:
            raise KeyError(f"Key `{key}` does not exist in config")

    @staticmethod
    def validate():
        if not Config.get('token'):
            raise NameError('ERROR: Token is not set.')
        if not Config.get('group_id'):
            raise NameError('ERROR: Group id is not set.')
