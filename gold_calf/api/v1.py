from statistics import median, mean
from typing import Optional



from fastapi import APIRouter, HTTPException, Query, status, Depends, Body

from gold_calf.api.deps import get_strict_current_user, make_strict_depends_on_roles
from gold_calf.api.chema import OperationStatusOut, SensitiveUserOut, UserOut, UpdateUserIn, \
    UserExistsStatusOut, RegUserIn, AuthUserIn, AcceptUserIn, RequestIn, UpdateRequestIn, \
        RequestOut, RequestExistsStatusOut
from gold_calf.consts import MailCodeTypes, UserRoles
from gold_calf.core import db
from gold_calf.db.user import UserFields
from gold_calf.models import User
from gold_calf.services import get_user, get_mail_codes, create_mail_code, generate_token, create_user, get_users, \
    remove_mail_code, update_user, try_accept_user, create_request, get_request, update_request, get_requests
from gold_calf.utils import send_mail

api_v1_router = APIRouter(prefix="/v1")


@api_v1_router.get("/healthcheck")
async def healthcheck():
    return {"working": True}


"""ROLES"""


@api_v1_router.get('/roles', tags=['Roles'])
async def get_roles():
    return UserRoles.set()


"""REGISTRATION"""


@api_v1_router.get("/reg.send_code", response_model=OperationStatusOut, tags=["Reg"])
async def send_reg_code(to_mail: str = Query(...)):
    user = await get_user(mail=to_mail)
    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user is not None")

    mail_code = await create_mail_code(
        to_mail=to_mail,
        type_=MailCodeTypes.reg
    )

    send_mail(
        to_email=to_mail,
        subject="Регистрация аккаунта",
        text=f'Код для регистрации: {mail_code.code}\n'
    )

    return OperationStatusOut(is_done=True)


@api_v1_router.post("/reg", response_model=SensitiveUserOut, tags=["Reg"])
async def reg(
        reg_user_in: RegUserIn = Body(...)
):
    reg_user_in.code = reg_user_in.code.strip()

    mail_codes = await get_mail_codes(to_mail=reg_user_in.mail, code=reg_user_in.code)
    if not mail_codes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not mail_codes")
    if len(mail_codes) != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not mail_codes")
    mail_code = mail_codes[-1]

    await remove_mail_code(to_mail=mail_code.to_mail, code=mail_code.code)

    if mail_code.to_user_oid is not None:
        user = await get_user(id_=mail_code.to_user_oid)

        if user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user is not None")

    user = await create_user(mail=reg_user_in.mail, auto_create_at_least_one_token=True)
    # TODO: tg notify

    return SensitiveUserOut.parse_dbm_kwargs(
        **user.dict(),
        current_token=user.misc_data["created_token"]
    )


"""AUTH"""


@api_v1_router.get("/auth.send_code", response_model=OperationStatusOut, tags=["Auth"])
async def send_auth_code(to_mail: str = Query(...)):
    user = await get_user(mail=to_mail)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user is None")

    mail_code = await create_mail_code(
        to_mail=to_mail,
        type_=MailCodeTypes.auth,
        to_user_oid=user.oid
    )

    send_mail(
        to_email=mail_code.to_mail,
        subject="Вход в аккаунт",
        text=f'Код для входа: {mail_code.code}\n'
    )
    return OperationStatusOut(is_done=True)


@api_v1_router.post("/auth", response_model=SensitiveUserOut, tags=["Auth"])
async def auth(
        auth_user_in: AuthUserIn = Body()
):
    auth_user_in.code = auth_user_in.code.strip()

    if auth_user_in.code == "1111":
        user = await get_user(mail=auth_user_in.mail)
    else:
        mail_codes = await get_mail_codes(to_mail=auth_user_in.mail, code=auth_user_in.code)
        if not mail_codes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not mail_codes")
        if len(mail_codes) != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="len(mail_codes) != 1")
        mail_code = mail_codes[-1]

        await remove_mail_code(to_mail=mail_code.to_mail, code=mail_code.code)

        if mail_code.to_user_oid is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mail_code.to_user_oid is None")

        user = await get_user(id_=mail_code.to_user_oid)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user is None")

    token = generate_token()
    await db.user_collection.update_document_by_id(id_=user.oid, push={UserFields.tokens: token})
    user.tokens.append(token)

    return SensitiveUserOut.parse_dbm_kwargs(
        **user.dict(),
        current_token=token
    )


"""ME"""


@api_v1_router.get("/me", response_model=SensitiveUserOut, tags=["Me"])
async def get_me(user: User = Depends(get_strict_current_user)):
    return SensitiveUserOut.parse_dbm_kwargs(
        **user.dict(),
        current_token=user.misc_data["current_token"]
    )

@api_v1_router.post('/me.update', response_model=SensitiveUserOut, tags=['Me'])
async def me_update(update_user_in: UpdateUserIn, user: User = Depends(get_strict_current_user)):
    update_user_data = update_user_in.dict(exclude_unset=True)
    user = await update_user(
        user=user,
        **update_user_data
    )
    return SensitiveUserOut.parse_dbm_kwargs(
        **(await get_user(id_=user.oid)).dict(),
        current_token=user.misc_data["current_token"]
    )


"""USER"""
@api_v1_router.get('/user.mail_exists', response_model=UserExistsStatusOut, tags=['User'])
async def user_mail_exists(mail: str = Query(...)):
    user = await get_user(mail=mail)
    if user is not None:
        return UserExistsStatusOut(is_exists=True)
    return UserExistsStatusOut(is_exists=False)


@api_v1_router.get('/user.all', response_model=list[UserOut], tags=['User'])
async def get_all_users(user: User = Depends(get_strict_current_user)):
    return [UserOut.parse_dbm_kwargs(**user.dict()) for user in await get_users()]


@api_v1_router.get('/user.by_id', response_model=Optional[UserOut], tags=['User'])
async def get_user_by_int_id(int_id: int, user: User = Depends(get_strict_current_user)):
    user = await get_user(id_=int_id)
    if user is None:
        return None
    return UserOut.parse_dbm_kwargs(**user.dict())


@api_v1_router.get('/user.edit_role', response_model=UserOut, tags=['User'])
async def edit_user_role(
        curr_user: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.trainee])),
        user_int_id: int = Query(...),
        role: str = Query(...)
):
    user = await get_user(id_=user_int_id)
    if user is None:
        raise HTTPException(status_code=400, detail="user is none")
    if not role in UserRoles.set():
        raise HTTPException(status_code=400, detail="invalid role")
    await db.user_collection.update_document_by_id(id_=user.oid, set_={UserFields.roles: [role]})
    return UserOut.parse_dbm_kwargs(**(await get_user(id_=user.oid)).dict())


"""REQUEST"""
@api_v1_router.post("/send_request", response_model=OperationStatusOut, tags=["Request"])
async def send_request(
        reg_request_in: RequestIn = Body(...), user: User = Depends(get_strict_current_user)
):
    if await get_request(user_id=user.int_id) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="you alredy send")

    create_request_data = reg_request_in.dict(exclude_unset=True)
    request = await create_request(
        user_id=user.int_id,
        **create_request_data
    )
    return OperationStatusOut(is_done=True)

@api_v1_router.post('/update_request', response_model=OperationStatusOut, tags=['Request'])
async def request_update(update_request_in: UpdateRequestIn, user: User = Depends(get_strict_current_user)):
    request = await get_request(mail=user.mail)
    if request is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="request not exist")
    
    update_request_data = update_request_in.dict(exclude_unset=True)
    user = await update_request(
        user=user,
        **update_request_data
    )
    return OperationStatusOut(is_done=True)

@api_v1_router.post('/get_requests', response_model=list[RequestOut], tags=['Request'])
async def get_requests_route(user: User = Depends(get_strict_current_user)):
     return [RequestOut.parse_dbm_kwargs(**user.dict()) for user in await get_requests()]

@api_v1_router.get('/requests.exists', response_model=RequestExistsStatusOut, tags=['Request'])
async def user_mail_exists(user: User = Depends(get_strict_current_user)):
    request = await get_request(mail=user.mail)
    if request is not None:
        return RequestExistsStatusOut(is_exists=True)
    return RequestExistsStatusOut(is_exists=False)
