import os
from dotenv import load_dotenv

load_dotenv()


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
