import csv

from gold_calf.api.chema import RequestIn, SensitiveUserOut
from gold_calf.db.request import RequestFields
from gold_calf.services import create_mail_code, get_mail_codes, remove_mail_code, get_user, create_user, get_request, create_request
from gold_calf.consts import MailCodeTypes

def parse_users_request(filepath: str) -> list[RequestIn]:
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        requests: RequestIn = list()
        index: int = 1
        for row in reader:
                request_dict = {
                        RequestFields.salary: row[RequestFields.salary],
                        RequestFields.remote_radio: row['remote_ratio'],
                        RequestFields.work_year: row[RequestFields.work_year],
                        RequestFields.experience_level: row[RequestFields.experience_level],
                        RequestFields.employment_type: row[RequestFields.employment_type],
                        RequestFields.job_title: row[RequestFields.job_title],
                }
                request_in: RequestIn = RequestIn(mail=f"{index}@uust-astrogame.ru", **request_dict)
                requests += [request_in]
                index += 1
    return requests

async def parse_users(filepath: str):
    requests: list[RequestIn] = parse_users_request(filepath=filepath)
    for user in requests:
        mail_code_reg = await create_mail_code(
            to_mail=user.mail,
            type_=MailCodeTypes.reg
        )
        mail_codes = await get_mail_codes(to_mail=user.mail, code=mail_code_reg.code)
        mail_code = mail_codes[-1]
        await remove_mail_code(to_mail=mail_code.to_mail, code=mail_code.code)
        if await get_user(mail=user.mail) is not None:
            print("Пользователь уже существует")
            user_created = await get_user(mail=user.mail)
        else:
            print("Пользователь создан")
            user_created = await create_user(mail=user.mail, auto_create_at_least_one_token=True)
        if await get_request(user_id=user_created.int_id) is not None:
            print("Вы уже посылали")
        else:
            print("Заявка отправлена")
            create_request_data = user.dict(exclude_unset=True)
            request = await create_request(
            user_id=user_created.int_id,
            **create_request_data
            )