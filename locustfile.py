from locust import events

from TaskSetLib.ViewCart import ViewCart
from UserLib.RegisteredHttpUser import RegisteredHttpUser
from CommonLib.UserLoader import UserLoader
from CommonLib.LogModule import Logger

@events.test_start.add_listener
def on_test_start(**kwargs):
    # if kwargs['environment'].parsed_options.logfile:
    #     Logger.init_logger(__name__, kwargs['environment'].parsed_options.logfile)
    # UserLoader.load_users()
    # EventInfluxHandlers.init_influx_client()
    UserLoader.load_users()
    Logger.log_message("......... Initiating Load Test .......")


@events.test_stop.add_listener
def on_test_stop(**kwargs):
    Logger.log_message("........ Load Test Completed ........")

class UserGroupA(RegisteredHttpUser):
    weight = 1
    RegisteredHttpUser.tasks = [ViewCart]

