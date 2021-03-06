"""Notify a user via telegram
"""
try:
    import telegram
except:
    pass
import logging
logger = logging.getLogger(__name__)


class TelegramNotifier():
    """Used to notify user of events via telegram.
    """

    def __init__(self, token, chat_id):
        """Initialize TelegramNotifier class

        Args:
            token (str): The telegram API token.
            chat_id (str): The chat ID you want the bot to send messages to.

        """

        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id

    def chunk_message(self, message, max_message_size):
        """ Chunks message so that it meets max size of integration.

        Args:
            message (str): The message to chunk.
            max_message_size (int): The max message length for the chunks.

        Returns:
            list: The chunked message.
        """

        chunked_message = list()
        if len(message) > max_message_size:
            split_message = message.splitlines(keepends=True)
            chunk = ''

            for message_part in split_message:
                temporary_chunk = chunk + message_part

                if max_message_size > len(temporary_chunk):
                    chunk += message_part
                else:
                    chunked_message.append(chunk)
                    chunk = ''
        else:
            chunked_message.append(message)

        return chunked_message

    def notify(self, message):
        """Send the notification.

        Args:
            message (str): The message to send.
        """

        max_message_size = 4096
        message_chunks = self.chunk_message(message=message, max_message_size=max_message_size)
        try:
            for message_chunk in message_chunks:
                self.bot.send_message(chat_id=self.chat_id, text=message_chunk)
            logger.info("Bot has sent message(s) to the chat group")
        except Exception as e:
            logger.error(e)
        
