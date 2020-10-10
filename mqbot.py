from telegram.ext import messagequeue as mq,

class MQBot(telegram.bot.Bot):
    """A subclass of Bot which delegates send method handling to MQ"""

    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        # noinspection PyBroadException
        try:
            self._msg_queue.stop()
        except Exception:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup` OPTIONAL arguments"""
        # logger.info("Sending queued message")
        return super(MQBot, self).send_message(*args, **kwargs)

    @mq.queuedmessage
    def send_photo(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup` OPTIONAL arguments"""
        # logger.info("Sending queued message")
        return super(MQBot, self).send_photo(*args, **kwargs)
        
    @mq.queuedmessage
    def send_document(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup` OPTIONAL arguments"""
        # logger.info("Sending queued message")
        return super(MQBot, self).send_document(*args, **kwargs)
