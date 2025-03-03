import uuid

import pytest
from tests.settings import DATABASE_URL

import saffier
from saffier import Registry
from saffier.db.connection import Database

database = Database(url=DATABASE_URL)
models = Registry(database=database)
nother = Registry(database=database)

pytestmark = pytest.mark.anyio


class User(saffier.Model):
    name = saffier.CharField(max_length=100)
    language = saffier.CharField(max_length=200, null=True)

    class Meta:
        registry = models


class Profile(saffier.Model):
    id = saffier.UUIDField(max_length=100, primary_key=True, default=uuid.uuid4)
    language = saffier.CharField(max_length=200, null=True)
    age = saffier.IntegerField()

    class Meta:
        registry = models
        tablename = "profiles"


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


async def test_model_default_primary_key():
    user = await User.query.create(name="Test", language="EN")
    users = await User.query.filter()

    assert user.pk == 1
    assert len(users) == 1


async def test_model_custom_primary_key():
    profile = await Profile.query.create(name="Test", language="EN", age=18)
    profiles = await Profile.query.filter()

    assert len(profiles) == 1
    assert profiles[0].pk == profile.pk
