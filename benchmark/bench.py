from locust import HttpUser, task, between
import json
from requests.models import Response

from benchmark.data import users

class UserHandler(HttpUser):
    wait_time = between(1, 3)  # Время ожидания между задачами
    host = users.host
    headers = {}
    
    def make_get_request(self, url: str) -> Response:
        return self.client.get(url=url, headers=self.headers)

    def make_post_request(self, url: str, payload: dict = {}) -> Response:
        return self.client.post(url=url, json=payload, headers=self.headers)

    def auth(self, mail: str, code: str) -> None:
            payload_auth = {
                "mail": mail,
                "code": code
            }
            response: Response = self.make_post_request("/auth", payload_auth)
            data = json.loads(response.text)
            token = data['current_token']
            self.headers = {
                'Authorization': f'Bearer {token}'
            }
    
    def send_request(self) -> Response:
        request_payload = {
        "mail": "string",
        "salary": 0,
        "remote_radio": "string",
        "work_year": 0,
        "experience_level": "string",
        "employment_type": "string",
        "job_title": "string"
        }
        return self.make_post_request("/send_request", request_payload)
    
    def update_request(self) -> Response:
        request_payload = {
        "mail": "New data",
        "salary": 100,
        "remote_radio": "New data",
        "work_year": 0,
        "experience_level": "New data",
        "employment_type": "New data",
        "job_title": "New data"
        }
        return self.make_post_request("/update_request", request_payload)

    def request_my(self) -> Response:
         return self.make_get_request("/request.my")
    
    def delete_request(self) -> Response:
        self.make_get_request(url="/request.delete_my")
    
    @task
    def healtcheck_task(self):
        response: Response = self.make_get_request("/healtcheck")
        print(f"Полученный результат: {response.text}")
    
    @task
    def roles_task(self):
        response: Response = self.make_get_request("/roles")
        print(f"Полученный результат: {response.text}")

    @task
    def auth_user_task(self):
        self.auth(mail=users.trainee["mail"], code=users.base_code_auth)
        print("Пользователь был авторизован")
    
    @task
    def user_mail_exist_task(self):
        response: Response = self.make_get_request(url=f"/user.mail_exists?mail={users.trainee['mail']}")
        print(f"Статус запроса: {response.status_code}")
        print(f"Результат: {response.text}")
        
    @task
    def user_all_task(self):
        self.auth(users.hr["mail"], users.base_code_auth)
        response_users = self.make_get_request("/user.all")
        print(f"Статус запроса: {response_users.status_code}")
        print(f"Результат: {response_users.text}")

    @task
    def send_request_task(self):
        self.auth(users.trainee["mail"], users.base_code_auth)
        response: Response = self.send_request()
        print(f"Статус запроса: {response.status_code}")
        print(f"Результат отправки заявки: {response.text}")
        self.delete_request()

    @task
    def update_request_task(self):
        self.auth(users.trainee["mail"], users.base_code_auth)
        self.send_request()
        response: Response = self.request_my()
        print(f"Статус запроса: {response.status_code}")
        print(f"Заявка до обновления: {response.text}")
        self.update_request()
        response_after: Response = self.request_my() 
        print(f"Статус запроса: {response_after.status_code}")
        print(f"Заявка после обновления: {response_after.text}")
        self.delete_request()

    @task
    def get_requests_task(self):
        self.auth(users.hr["mail"], users.base_code_auth)
        response: Response = self.make_post_request("/get_requests")
        print(f"Статус запроса: {response.status_code}")
        print(f"Заявки: {response.text}")

