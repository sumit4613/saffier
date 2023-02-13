import pytest
from tests.settings import DATABASE_URL

import saffier
from saffier import Registry
from saffier.core.db import Database

database = Database(url=DATABASE_URL)
models = Registry(database=database)
nother = Registry(database=database)

pytestmark = pytest.mark.anyio

from uuid import uuid4


class User(saffier.Model):
    name = saffier.CharField(max_length=100)
    language = saffier.CharField(max_length=200, null=True)

    class Meta:
        registry = models


class Profile(saffier.Model):
    age = saffier.IntegerField()

    class Meta:
        registry = models
        name = "profiles"


@pytest.fixture(autouse=True, scope="function")
async def create_test_database():
    await models.create_all()
    yield
    await models.drop_all()


@pytest.fixture(autouse=True)
async def rollback_connections():
    with database.force_rollback():
        async with database:
            yield


async def test_model_inheritance():
    breakpoint()
    user = await User.query.create(name="Test", language="EN")
    profile = await Profile.query.create(name="Test2", language="PT", age=23)

    users = await User.query.all()
    profiles = await Profile.query.all()

    assert len(users) == 1
    assert len(profiles) == 1
