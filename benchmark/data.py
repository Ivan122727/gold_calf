import os
from dotenv import load_dotenv


class Users:
    def __init__(self) -> None:
        load_dotenv("./benchmark_users.env")
        self.base_code_auth = "1111"
        self.trainee = {
            "mail": os.getenv("trainee_mail")
        }
        self.hr = {
            "mail": os.getenv("hr_mail")
        }
        self.dev = {
            "mail": os.getenv("dev_mail")
        }

users = Users()