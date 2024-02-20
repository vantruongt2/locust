from locust import events

from TaskSetLib.ViewCart import ViewCart
from UserLib.RegisteredHttpUser import RegisteredHttpUser
from CommonLib.UserLoader import UserLoader
from CommonLib.LogModule import Logger

@events.test_start.add_listener
def on_test_start(**kwargs):
    UserLoader.load_users()
    Logger.log_message("......... Initiating Load Test .......")


@events.test_stop.add_listener
def on_test_stop(**kwargs):
    Logger.log_message("........ Load Test Completed ........")

class UserGroupA(RegisteredHttpUser):
    weight = 1
    RegisteredHttpUser.tasks = [ViewCart]

