import logging

from gold_calf.consts import UserRoles, Modes
from gold_calf.core import db, settings
from gold_calf.db.db import CannotConnectToDb

log = logging.getLogger(__name__)


async def prepare_db():
    try:
        await db.check_conn()
    except CannotConnectToDb as e:
        log.exception(e)
        raise e
    await db.ensure_all_indexes()
    log.info("db conn is good")


async def on_startup(*args, **kwargs):
    await prepare_db()


async def on_shutdown(*args, **kwargs):
    pass