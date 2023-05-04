import pymongo

from gold_calf.db.base import BaseCollection, BaseFields


class UserFields(BaseFields):
    mail = "mail"
    tokens = "tokens"
    roles = "roles"
    salary = "salary"
    remote_radio = "remote_radio"
    work_year = "work_year"
    experience_level = "experience_level"
    employment_type = "employment_type"
    job_title = "job_title"
    is_accepted = "is_accepted"

class UserCollection(BaseCollection):
    COLLECTION_NAME = "user"

    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(UserFields.mail, pymongo.ASCENDING)],
            unique=True, sparse=True
        )
