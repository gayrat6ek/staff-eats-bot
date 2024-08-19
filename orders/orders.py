import requests
from dotenv import load_dotenv
import os
load_dotenv()

BACKEND_TOKEN = os.getenv('BACKEND_TOKEN')
BASE_URL = os.getenv('BASE_URL')


def get_user(user_id):
    response = requests.get(f"{BASE_URL}/api/v1/clients", headers={"Authorization": f"Bearer {BACKEND_TOKEN}"}, params={"telegram_id": user_id})
    return response.json()


def create_client(data):
    response = requests.post(f"{BASE_URL}/api/v1/clients", headers={"Authorization": f"Bearer {BACKEND_TOKEN}"}, json=data)
    return response.json()

def get_department(password):
    response = requests.get(f"{BASE_URL}/api/v1/departments", headers={"Authorization": f"Bearer {BACKEND_TOKEN}"}, params={"password": password})
    return response.json()



def create_order(data):
    response = requests.post(f"{BASE_URL}/api/v1/orders", headers={"Authorization": f"Bearer {BACKEND_TOKEN}"}, json=data)
    return response.json()


def logout_reqeust(data):
    response = requests.put(f"{BASE_URL}/api/v1/clients/logout",headers={"Authorization": f"Bearer {BACKEND_TOKEN}"},  json=data)
    return response.json()


def client_update(data):
    response = requests.put(f"{BASE_URL}/api/v1/clients", headers={"Authorization": f"Bearer {BACKEND_TOKEN}"},  json=data)
    return response.json()