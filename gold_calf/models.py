from __future__ import annotations

from datetime import datetime
from ipaddress import IPv4Interface, IPv4Address
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, Extra
from pydantic.fields import ModelField

from gold_calf.consts import RolesType
from gold_calf.db.base import BaseFields, Document
from gold_calf.db.mailcode import MailCodeFields
from gold_calf.db.user import UserFields
from gold_calf.utils import roles_to_list


class BaseDBM(BaseModel):
    misc_data: dict[Any, Any] = Field(default={})

    # db fields
    oid: Optional[ObjectId] = Field(alias=BaseFields.oid)
    int_id: Optional[int] = Field(alias=BaseFields.int_id)
    created: Optional[datetime] = Field(alias=BaseFields.created)

    class Config:
        extra = Extra.ignore
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.timestamp()
        }

    def to_json(self, **kwargs) -> str:
        kwargs["indent"] = 2
        kwargs["ensure_ascii"] = False
        return self.json(**kwargs)

    def to_dict(self, only_db_fields: bool = True, **kwargs) -> dict:
        data = self.dict(**kwargs)
        if only_db_fields is True:
            for f in self.__fields__.values():
                f: ModelField
                if f.alias not in data:
                    continue
                if f.has_alias is False:
                    del data[f.alias]
                    continue
        return data

    @classmethod
    def parse_document(cls, doc: Document) -> BaseDBM:
        """get only fields that has alias and exists in doc"""
        doc_to_parse = {}
        for f in cls.__fields__.values():
            f: ModelField
            if f.has_alias is False:
                continue
            if f.alias not in doc:
                continue
            doc_to_parse[f.alias] = doc[f.alias]
        return cls.parse_obj(doc_to_parse)

    def document(self) -> Document:
        doc = self.dict(by_alias=True, exclude_none=False, exclude_unset=False, exclude_defaults=False)
        for f in self.__fields__.values():
            f: ModelField
            if f.alias not in doc:
                continue
            if f.has_alias is False:
                del doc[f.alias]
                continue
            if doc[f.alias] is None:
                continue
            if f.outer_type_ in [IPv4Interface, IPv4Address]:
                doc[f.alias] = str(doc[f.alias])
            elif f.outer_type_ in [list[IPv4Interface], list[IPv4Address]]:
                doc[f.alias] = [str(ip) for ip in doc[f.alias]]
        return doc


class User(BaseDBM):
    # db fields
    mail: Optional[str] = Field(alias=UserFields.mail)    
    tokens: list[str] = Field(alias=UserFields.tokens, default=[])
    roles: list[str] = Field(alias=UserFields.roles, default=[])
    salary: Optional[int] = Field(alias=UserFields.salary)
    remote_radio: Optional[str] = Field(alias=UserFields.remote_radio)
    work_year: Optional[int] = Field(alias=UserFields.work_year)
    experience_level: Optional[str] = Field(alias=UserFields.experience_level)
    employment_type: Optional[str] = Field(alias=UserFields.employment_type)
    job_title: Optional[str] = Field(alias=UserFields.job_title)
    is_accepted: Optional[bool] = Field(alias=UserFields.is_accepted)
    # direct linked models
    # ...

    # indirect linked models
    mail_codes: list[MailCode] = Field(default=[])

    def compare_roles(self, needed_roles: RolesType) -> bool:
        needed_roles = roles_to_list(needed_roles)
        return bool(set(needed_roles) & set(self.roles))



class MailCode(BaseDBM):
    # db fields
    to_mail: str = Field(alias=MailCodeFields.to_mail)
    code: str = Field(alias=MailCodeFields.code)
    type: str = Field(alias=MailCodeFields.type)  # use MailCodeTypes
    to_user_oid: Optional[ObjectId] = Field(alias=MailCodeFields.to_user_oid)

    # direct linked models
    to_user: Optional[User] = Field(default=None)
