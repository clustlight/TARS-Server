import logging
import requests
from time import sleep
import database
from twitcasting import Twitcasting


def fetch_scheduler(port):
    """
    Periodically fetches subscription data and updates the database.

    Args:
        port (str): The port number of the server to fetch subscriptions from.
    """
    logger = logging.getLogger("Subscriptions")
    sleep(3)
    twitcasting = Twitcasting()

    while True:
        fetch_count = 0
        logger.debug("Retrieving subscriptions...")
        response = requests.get(f"http://localhost:{port}/subscriptions")
        users = response.json()["users"]
        logger.debug(f"{len(users)} user(s) found")
        for user in users:
            database.set_subscription_user(user)

        for user in users:
            fetch_count += 1
            logger.debug(f"Retrieving user_id: [{user}]'s metadata...")
            user_data_response = twitcasting.get_user_info(user)
            if user_data_response[0]:
                logger.debug(f"{user} is {user_data_response[1]['user']['screen_id']}")
                database.update_user(user_data_response[1])

            if fetch_count == 5:
                fetch_count = 0
                sleep(60)
            else:
                sleep(1)