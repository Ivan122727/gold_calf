from typing import Union

from gold_calf.helpers import SetForClass


class MailCodeTypes(SetForClass):
    reg = "reg"
    auth = "auth"


class UserRoles(SetForClass):
    hr = "hr"
    trainee = "trainee"
    dev = "dev"


RolesType = Union[set[str], list[str], str]


class Modes(SetForClass):
    prod = "prod"
    dev = "dev"
