import logging
from time import sleep

from usecases import refresh_user, sync_subscriptions


def fetch_scheduler():
    """
    Periodically fetches subscription data and updates the database.
    """
    logger = logging.getLogger("Subscriptions")
    sleep(3)

    while True:
        fetch_count = 0
        logger.debug("Retrieving subscriptions...")
        result = sync_subscriptions()
        if not result.ok:
            logger.error(f"Failed to retrieve subscriptions: {result.error}")
            sleep(60)
            continue

        users = result.data["users"]
        logger.debug(f"{len(users)} user(s) found")

        for user in users:
            fetch_count += 1
            logger.debug(f"Retrieving user_id: [{user}]'s metadata...")
            user_result = refresh_user(user)
            if user_result.ok:
                logger.debug(f"{user} is {user_result.data['user']['screen_id']}")
            else:
                logger.error(f"Failed to refresh user {user}: {user_result.error}")

            if fetch_count == 5:
                fetch_count = 0
                sleep(60)
            else:
                sleep(1)