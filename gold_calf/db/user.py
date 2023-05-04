import pymongo

from gold_calf.db.base import BaseCollection, BaseFields


class UserFields(BaseFields):
    tokens = "tokens"
    roles = "roles"
    is_accepted = "is_accepted"
    mail = "mail"

class UserCollection(BaseCollection):
    COLLECTION_NAME = "user"

    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(UserFields.int_id, pymongo.ASCENDING), (UserFields.mail, pymongo.ASCENDING)],
            unique=True, sparse=True
        )
