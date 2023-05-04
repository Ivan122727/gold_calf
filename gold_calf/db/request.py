import pymongo

from gold_calf.db.base import BaseCollection, BaseFields


class RequestFields(BaseFields):
    mail = "mail"
    salary = "salary"
    remote_radio = "remote_radio"
    work_year = "work_year"
    experience_level = "experience_level"
    employment_type = "employment_type"
    job_title = "job_title"
    is_accepted = "is_accepted"
    user_id = "user_id"

class RequestCollection(BaseCollection):
    COLLECTION_NAME = "request"

    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(RequestFields.user_id, pymongo.ASCENDING), (RequestFields.int_id, pymongo.ASCENDING)],
            unique=True, sparse=True
        )
