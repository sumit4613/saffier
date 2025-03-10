import datetime
from enum import Enum

import pytest
from asyncpg.exceptions import UniqueViolationError
from tests.settings import DATABASE_URL

import saffier
from saffier.db.connection import Database

pytestmark = pytest.mark.anyio

database = Database(DATABASE_URL)
models = saffier.Registry(database=database)


def time():
    return datetime.datetime.now().time()


class StatusEnum(Enum):
    DRAFT = "Draft"
    RELEASED = "Released"


class BaseModel(saffier.Model):
    class Meta:
        registry = models


class User(BaseModel):
    name = saffier.CharField(max_length=255, unique=True)
    email = saffier.CharField(max_length=60)


@pytest.fixture(autouse=True, scope="module")
async def create_test_database():
    await models.create_all()
    yield
    await models.drop_all()


@pytest.fixture(autouse=True)
async def rollback_transactions():
    with database.force_rollback():
        async with database:
            yield


@pytest.mark.skipif(database.url.dialect == "mysql", reason="Not supported on MySQL")
async def test_unique():
    await User.query.create(name="Tiago", email="test@example.com")

    with pytest.raises(UniqueViolationError):
        await User.query.create(name="Tiago", email="test2@example.come")
