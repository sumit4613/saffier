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


class Profile(User):
    age = saffier.IntegerField()

    class Meta:
        registry = models
        tablename = "profiles"


class Contact(Profile):
    age = saffier.CharField(max_length=255)
    address = saffier.CharField(max_length=255)

    class Meta:
        registry = models
        tablename = "contacts"


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
    user = await User.query.create(name="Test", language="EN")
    profile = await Profile.query.create(name="Test2", language="PT", age=23)

    users = await User.query.all()
    profiles = await Profile.query.all()

    assert len(users) == 1
    assert len(profiles) == 1
    assert users[0].pk == user.pk
    assert profiles[0].pk == profile.pk


async def test_model_triple_inheritace():
    contact = await Contact.query.create(name="Test", language="EN", age="25", address="Far")

    contacts = await Contact.query.all()

    assert len(contacts) == 1
    assert contact.age == "25"
    assert contact.address == "Far"
