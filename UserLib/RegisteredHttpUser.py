from locust import between, clients
from CommonLib.LogModule import *
from locust.exception import StopUser
from CommonLib.UserLoader import UserLoader
from UserLib.AbstractUser import AbstractUser
from bs4 import BeautifulSoup

class RegisteredHttpUser(AbstractUser):
    wait_time = between(1, 2)
    abstract = True

    def verify_login_success(self, response, email):
        print(f'status code is: {response.status_code}')
        if response.status_code != 302 or 'Authentication failed.' in response.text:
            response.failure("Failed to login, user: " + email + " Status Code : " + str(response.status_code))
            raise StopUser()
        return True

    def getToken(self):
        with self.client.get("/", headers={}, data={}) as response:
            csrftoken = response.cookies.get_dict()['csrftoken']
            soup = BeautifulSoup(response.content, 'html.parser')
            soup = soup.find(['body'])
            csrfmiddlewaretoken = soup.select_one('input[name=csrfmiddlewaretoken]')['value']
            return {'csrftoken': csrftoken, 'csrfmiddlewaretoken': csrfmiddlewaretoken}

    def on_start(self):
        # TODO: Fetch one user from user list and login, store cookie and user info
        user_obj = UserLoader.get_user()
        user_token = self.getToken()

        form_data = {'email': user_obj['username'], 'password': user_obj['password'],
                     'csrfmiddlewaretoken': user_token['csrfmiddlewaretoken']}

        header = {'authority': 'automationexercise.com',
                  'Content-Type': 'application/x-www-form-urlencoded',
                  'origin': 'https://automationexercise.com',
                  'referer': 'https://automationexercise.com/login',
                  'Cookie': f'csrftoken={user_token["csrftoken"]}'
                  }

        with self.client.post("/login", form_data, headers=header, allow_redirects=False,
                              catch_response=True) as response:
            if self.verify_login_success(response, user_obj['username']):
                Logger.log_message("Login successful with user : " + user_obj['username'], LogType.INFO)
                user_cookie = f'csrftoken={user_token["csrftoken"]};sessionid={response.cookies.get_dict()["sessionid"]}'
                super().set_email(user_obj['username'])
                super().set_cookie(user_cookie)

    def on_stop(self):
        # TODO: Logout user from server when load test ends
        pass
