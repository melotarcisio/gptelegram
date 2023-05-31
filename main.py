"""
Main file for the bot.
"""
from time import sleep

from modules.message import MessageHandler, get_updates
from modules.context import logger

message_handler = MessageHandler()


def bot_loop():
    updates = get_updates()
    off_set = max([*map(
        lambda x: x.update_id,
        updates
    ), 0])
    while True:
        sleep(1)
        try:
            updates = get_updates(off_set + 1)
            for update in updates:
                if update.update_id > off_set:
                    off_set = update.update_id
                # TODO: handle message in a separate thread
                message_handler.handle(update)
        except Exception as e:
            logger.send(str(e))


if __name__ == '__main__':
    bot_loop()
