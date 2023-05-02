import os
import pathlib
from typing import Optional
from urllib.parse import quote

from pydantic import BaseSettings

from gold_calf.consts import Modes

BASE_DIRPATH: str = str(pathlib.Path(__file__).parent.parent)
ENV_FILEPATH: str = os.path.join(BASE_DIRPATH, '.env')


class Settings(BaseSettings):
    api_title: str = "GOLD_CALF API"
    api_prefix: str = "/api"

    mongo_user: Optional[str] = None
    mongo_password: Optional[str] = None
    mongo_host: str
    mongo_port: int = 27017
    mongo_auth_db: Optional[str] = None
    mongo_db_name: str = "gold_calf"

    mailru_login: str
    mailru_password: str
    mailru_server: str = "smtp.mail.ru"
    mailru_port: int = 465

    cache_dirname: str = "cache"
    cache_dirpath: str = os.path.join(BASE_DIRPATH, cache_dirname)

    front_domain: str = "https://uunit-gaming.ru"

    mode: str = Modes.dev

    emulate_mail_sending: bool = False

    @property
    def mongo_uri(self) -> str:
        mongo_uri = f'mongodb://'
        if self.mongo_user is not None:
            mongo_uri += self.mongo_user
            if self.mongo_password is not None:
                mongo_uri += ":" + quote(self.mongo_password) + "@"
        mongo_uri += self.mongo_host + ":" + str(self.mongo_port)
        if self.mongo_auth_db is not None:
            mongo_uri += f"/?authSource={self.mongo_auth_db}"
        return mongo_uri

    class Config:
        if os.path.exists(ENV_FILEPATH):
            env_file = ENV_FILEPATH

    log_filepath: str = os.path.join(BASE_DIRPATH, "story.log")


if __name__ == '__main__':
    print(Settings())
