import asyncio

from gold_calf.cache_dir import CacheDir
from gold_calf.db.db import DB
from gold_calf.settings import Settings

settings = Settings()
db = DB(mongo_uri=settings.mongo_uri, mongo_db_name=settings.mongo_db_name)
cache_dir = CacheDir(settings.cache_dirpath)
