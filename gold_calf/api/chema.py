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
    roles: list[str] = []
    mail: Optional[str]
    is_accepted: bool


class RequestOut(BaseOutDBMSchema):
    mail: str
    salary: Optional[int] = None
    remote_radio: Optional[str] = None
    work_year: Optional[int] = None
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    job_title: Optional[str] = None
    is_accepted: bool
    user_id: int

class SensitiveUserOut(UserOut):
    tokens: list[str]
    current_token: str


class OperationStatusOut(BaseSchemaOut):
    is_done: bool


class ExistsStatusOut(BaseSchemaOut):
    is_exists: bool


class UserExistsStatusOut(BaseSchemaOut):
    is_exists: bool


class RegUserIn(BaseSchemaIn):
    mail: str
    code: str


class AuthUserIn(BaseSchemaIn):
    mail: str
    code: str


class UpdateUserIn(BaseSchemaIn):
    is_accepted: Optional[bool]

class UpdateRequestIn(BaseSchemaIn):
    salary: Optional[int] = None
    remote_radio: Optional[str] = None
    work_year: Optional[int] = None
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    job_title: Optional[str] = None
    mail: Optional[str] = None

class AcceptUserIn(BaseSchemaIn):
    is_accepted: Optional[bool]
    requester_id: int


class RequestIn(BaseSchemaIn):
    mail: str
    salary: int
    remote_radio: str
    work_year: int
    experience_level: str
    employment_type: str
    job_title: str

class RequestExistsStatusOut(BaseSchemaOut):
    is_exists: bool

class RequestAcceptIn(BaseSchemaIn):
    request_id: int
    is_accepted: bool