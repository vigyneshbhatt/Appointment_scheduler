from ApiHandler import ApiHandler
from Scheduler import Scheduler


if __name__ == "__main__":
    api_token = "5d1dc8a8-30ba-45d7-853b-e25d81488c8e"

    api_handler = ApiHandler(api_token)
    scheduler = Scheduler(api_handler)
    scheduler.schedule()