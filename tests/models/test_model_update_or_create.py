import pytest
from tests.settings import DATABASE_URL

import saffier
from saffier.db.connection import Database

database = Database(url=DATABASE_URL)
models = saffier.Registry(database=database)

pytestmark = pytest.mark.anyio


class User(saffier.Model):
    id = saffier.IntegerField(primary_key=True)
    name = saffier.CharField(max_length=100)
    language = saffier.CharField(max_length=200, null=True)

    class Meta:
        registry = models


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


async def test_model_update_or_create():
    user, created = await User.query.update_or_create(
        name="Test", language="English", defaults={"name": "Jane"}
    )
    assert created is True
    assert user.name == "Jane"
    assert user.language == "English"

    user, created = await User.query.update_or_create(
        name="Jane", language="English", defaults={"name": "Test"}
    )
    assert created is False
    assert user.name == "Test"
    assert user.language == "English"
