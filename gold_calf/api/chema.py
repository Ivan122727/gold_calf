from __future__ import annotations

from datetime import datetime
from typing import Optional, Any

from bson import ObjectId
from pydantic import BaseModel, Extra


class BaseSchema(BaseModel):
    class Config:
        extra = Extra.ignore
        arbitrary_types_allowed = True
        allow_population_by_field_name = True


class BaseSchemaOut(BaseSchema):
    misc: dict[str, Any] = {}


class BaseOutDBMSchema(BaseSchemaOut):
    oid: str
    int_id: int
    created: datetime

    @classmethod
    def parse_dbm_kwargs(
            cls,
            **kwargs
    ):
        res = {}
        for k, v in kwargs.items():
            if isinstance(v, ObjectId):
                v = str(v)
            res[k] = v
        return cls(**res)


class BaseSchemaIn(BaseSchema):
    pass


class UserOut(BaseOutDBMSchema):
    mail: str
    roles: list[str] = []
    salary: Optional[int] = None
    remote_radio: Optional[str] = None
    work_year: Optional[int] = None
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    job_title: Optional[str] = None
    is_accepted: bool


class SensitiveUserOut(UserOut):
    tokens: list[str]
    current_token: str


class OperationStatusOut(BaseSchemaOut):
    is_done: bool


class ExistsStatusOut(BaseSchemaOut):
    is_exists: bool


class UpdateUserIn(BaseSchemaIn):
    salary: Optional[int] = None
    remote_radio: Optional[str] = None
    work_year: Optional[int] = None
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    job_title: Optional[str] = None
    is_accepted: Optional[bool]

class AcceptUserIn(BaseSchemaIn):
    is_accepted: Optional[bool]
    requester_id: int

class UserExistsStatusOut(BaseSchemaOut):
    is_exists: bool


class RegUserIn(BaseSchemaIn):
    mail: str
    code: str


class AuthUserIn(BaseSchemaIn):
    mail: str
    code: str
