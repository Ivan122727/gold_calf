import logging
import os
from random import randint
from typing import Union, Optional
from statistics import mean, median
import binascii

import pymongo
from bson import ObjectId

from gold_calf.consts import UserRoles, RolesType
from gold_calf.core import db
from gold_calf.db.base import Id
from gold_calf.db.mailcode import MailCodeFields
from gold_calf.db.user import UserFields
from gold_calf.helpers import NotSet, is_set
from gold_calf.models import User, MailCode
from gold_calf.utils import roles_to_list

"""USER LOGIC"""

log = logging.getLogger()


async def update_user(
        *,
        user: Union[User, ObjectId],
        salary: Union[NotSet, Optional[int]] = NotSet,
        remote_radio: Union[NotSet, Optional[str]] = NotSet,
        work_year: Union[NotSet, Optional[int]] = NotSet,
        experience_level: Union[NotSet, Optional[str]] = NotSet,
        employment_type: Union[NotSet, Optional[str]] = NotSet,
        job_title: Union[NotSet, Optional[str]] = NotSet
) -> User:
    if isinstance(user, User):
        pass
    elif isinstance(user, ObjectId):
        user = await get_user(id_=user)
    else:
        raise TypeError("bad type for user")

    if user is None:
        raise ValueError("user is None")

    set_ = {}
    if is_set(salary):
        set_[UserFields.salary] = salary
    if is_set(remote_radio):
        if remote_radio is not None:
            remote_radio = remote_radio.strip()
        set_[UserFields.remote_radio] = remote_radio
    if is_set(work_year):
        set_[UserFields.work_year] = work_year
    if is_set(experience_level):
        if experience_level is not None:
            experience_level = experience_level.strip()
        set_[UserFields.experience_level] = experience_level
    if is_set(employment_type):
        if employment_type is not None:
            employment_type = employment_type.strip()
        set_[UserFields.employment_type] = employment_type
    if is_set(job_title):
        if job_title is not None:
            job_title = job_title.strip()
        set_[UserFields.job_title] = job_title

    if set_:
        await db.user_collection.update_document_by_id(
            id_=user.oid,
            set_=set_
        )

        if is_set(salary):
            user.salary = salary
        if is_set(remote_radio):
            user.remote_radio = remote_radio
        if is_set(work_year):
            user.work_year = work_year
        if is_set(experience_level):
            set_[UserFields.experience_level] = experience_level
        if is_set(employment_type):
            user.employment_type = employment_type
        if is_set(job_title):
            user.job_title = job_title

    return user


def generate_token() -> str:
    res = binascii.hexlify(os.urandom(20)).decode() + str(randint(10000, 1000000))
    return res[:128]


async def create_user(
        *,
        mail: str,
        tokens: Optional[list[str]] = None,
        auto_create_at_least_one_token: bool = True,
        salary: Optional[int] = None,
        remote_radio: Optional[str] = None,
        work_year: Optional[int] = None,
        experience_level: Optional[str] = None,
        employment_type: Optional[str] = None,
        job_title: Optional[str] = None,
        roles: RolesType = None
):
    if roles is None:
        roles = [UserRoles.trainee]
    else:
        roles = roles_to_list(roles)

    created_token: Optional[str] = None
    if tokens is None:
        tokens = []
        if auto_create_at_least_one_token is True:
            created_token = generate_token()
            tokens.append(created_token)

    mail = mail.strip()

    if remote_radio is not None:
        remote_radio = remote_radio.strip()

    if experience_level is not None:
        experience_level = experience_level.strip()

    if employment_type is not None:
        employment_type = employment_type.strip()

    if job_title is not None:
        job_title = job_title.strip()

    doc_to_insert = {
        UserFields.mail: mail,
        UserFields.salary: salary,
        UserFields.remote_radio: remote_radio,
        UserFields.work_year: work_year,
        UserFields.tokens: tokens,
        UserFields.experience_level: experience_level,
        UserFields.employment_type: employment_type,
        UserFields.job_title: job_title,
        UserFields.roles: roles
    }
    inserted_doc = await db.user_collection.insert_document(doc_to_insert)
    created_user = User.parse_document(inserted_doc)
    created_user.misc_data["created_token"] = created_token
    return created_user


async def get_user(
        *,
        id_: Optional[Id] = None,
        mail: Optional[str] = None,
        token: Optional[str] = None,
) -> Optional[User]:
    filter_ = {}
    if id_ is not None:
        filter_.update(db.user_collection.create_id_filter(id_=id_))
    if mail is not None:
        filter_[UserFields.mail] = mail
    if token is not None:
        filter_[UserFields.tokens] = {"$in": [token]}

    if not filter_:
        raise ValueError("not filter_")

    doc = await db.user_collection.find_document(filter_=filter_)
    if doc is None:
        return None
    return User.parse_document(doc)


async def get_users(*, roles: Optional[list[str]] = None) -> list[User]:
    users = [User.parse_document(doc) async for doc in db.user_collection.create_cursor()]
    if roles is not None:
        users = [user for user in users if user.compare_roles(roles)]
    return users


async def remove_token(*, client_id: Id, token: str):
    await db.user_collection.motor_collection.update_one(
        db.user_collection.create_id_filter(id_=client_id),
        {'$pull': {UserFields.tokens: token}}
    )


"""MAIL CODE LOGIC"""


async def remove_mail_code(
        *,
        id_: Optional[Id] = None,
        to_mail: Optional[str] = None,
        code: Optional[str] = None
):
    filter_ = {}
    if id_ is not None:
        filter_.update(db.mail_code_collection.create_id_filter(id_=id_))
    if to_mail is not None:
        filter_[MailCodeFields.to_mail] = to_mail
    if code is not None:
        filter_[MailCodeFields.code] = code

    if not filter_:
        raise ValueError("not filter_")

    await db.mail_code_collection.remove_document(
        filter_=filter_
    )


def _generate_mail_code() -> str:
    return str(randint(1, 9)) + str(randint(1, 9)) + str(randint(1, 9)) + str(randint(1, 9))


async def generate_unique_mail_code() -> str:
    mail_code = _generate_mail_code()
    while await db.mail_code_collection.document_exists(filter_={MailCodeFields.code: mail_code}):
        mail_code = _generate_mail_code()
    return mail_code


async def get_mail_codes(
        *,
        id_: Optional[Id] = None,
        to_mail: Optional[str] = None,
        code: Optional[str] = None,
        type_: Optional[str] = None,  # use MailCodeTypes
        to_user_oid: Union[NotSet, Optional[ObjectId]] = NotSet
) -> list[MailCode]:
    filter_ = {}
    if id_ is not None:
        filter_.update(db.mail_code_collection.create_id_filter(id_=id_))
    if to_mail is not None:
        filter_[MailCodeFields.to_mail] = to_mail
    if code is not None:
        filter_[MailCodeFields.code] = code
    if type_ is not None:
        filter_[MailCodeFields.type] = type_
    if is_set(to_user_oid):
        filter_[MailCodeFields.to_user_oid] = to_user_oid

    cursor = db.mail_code_collection.create_cursor(
        filter_=filter_,
        sort_=[(MailCodeFields.created, pymongo.DESCENDING)],
    )

    return [MailCode.parse_document(doc) async for doc in cursor]


async def create_mail_code(
        *,
        to_mail: str,
        code: str = None,
        type_: str,  # use MailCodeTypes
        to_user_oid: Optional[ObjectId] = None
) -> MailCode:
    to_user: Optional[User] = None
    if to_user_oid is not None:
        to_user = await get_user(id_=to_user_oid)
        if to_user is None:
            raise Exception("to_user is None")

    if code is None:
        code = await generate_unique_mail_code()

    doc_to_insert = {
        MailCodeFields.to_mail: to_mail,
        MailCodeFields.code: code,
        MailCodeFields.type: type_,
        MailCodeFields.to_user_oid: to_user_oid
    }
    inserted_doc = await db.mail_code_collection.insert_document(doc_to_insert)
    created_mail_code = MailCode.parse_document(inserted_doc)

    created_mail_code.to_user = to_user

    return created_mail_code
