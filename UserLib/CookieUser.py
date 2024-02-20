import requests
from bs4 import BeautifulSoup

class UserCookie:
    login_url = "https://automationexercise.com/login"

    @staticmethod
    def getSession():
        return requests.session()

    @staticmethod
    def getToken(session):
        req = session.request("GET", UserCookie.login_url, headers={}, data={})
        csrftoken = req.cookies.get_dict()['csrftoken']
        soup = BeautifulSoup(req.content, 'html.parser')
        soup = soup.find(['body'])
        csrfmiddlewaretoken = soup.select_one('input[name=csrfmiddlewaretoken]')['value']
        return {'csrftoken': csrftoken, 'csrfmiddlewaretoken': csrfmiddlewaretoken}

    @staticmethod
    def getCookie(session, token_dict):
        csrftoken = token_dict['csrftoken']
        csrfmiddlewaretoken = token_dict['csrfmiddlewaretoken']

        payload = {
            'email': 'locust_user_1@gmail.com',
            'password': 'locust_user_1',
            'csrfmiddlewaretoken': f'{csrfmiddlewaretoken}'
        }

        headers = {'authority': 'automationexercise.com',
                   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7;',
                   'accept-language': 'en-US,en;q=0.9', 'cache-control': 'max-age=0',
                   'Content-Type': 'application/x-www-form-urlencoded', 'origin': 'https://automationexercise.com',
                   'referer': 'https://automationexercise.com/login', 'Cookie': f'csrftoken={csrftoken}'}

        response = session.request("POST", UserCookie.login_url, headers=headers, data=payload, allow_redirects=False)
        sessionid = response.cookies.get_dict()['sessionid']
        valid_cookie = f'csrftoken={csrftoken};sessionid={sessionid}'
        return valid_cookie
