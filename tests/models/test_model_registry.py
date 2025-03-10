import pytest
from tests.settings import DATABASE_URL

import saffier
from saffier import Registry
from saffier.db.connection import Database

database = Database(url=DATABASE_URL)
models = Registry(database=database)
nother = Registry(database=database)

pytestmark = pytest.mark.anyio


class BaseUser(saffier.Model):
    name = saffier.CharField(max_length=100)
    language = saffier.CharField(max_length=200, null=True)

    class Meta:
        registry = models
        abstract = True


class Profile(BaseUser):
    age = saffier.IntegerField()

    def __str__(self):
        return f"Age: {self.age}, Name:{self.name}"


class BaseUserNonAbstract(saffier.Model):
    name = saffier.CharField(max_length=100)
    language = saffier.CharField(max_length=200, null=True)

    class Meta:
        registry = models


class AnotherProfile(BaseUserNonAbstract):
    age = saffier.IntegerField()

    def __str__(self):
        return f"Age: {self.age}, Name:{self.name}"


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


async def test_meta_inheritance_registry():
    await Profile.query.create(name="test", language="EN", age=23)

    await Profile.query.all()


async def test_meta_inheritance_registry_non_abstract():
    await AnotherProfile.query.create(name="test", language="EN", age=23)

    await AnotherProfile.query.all()
