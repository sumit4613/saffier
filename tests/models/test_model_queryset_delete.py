import pytest
from tests.settings import DATABASE_URL

import saffier
from saffier.db.connection import Database

database = Database(url=DATABASE_URL)
models = saffier.Registry(database=database)

pytestmark = pytest.mark.anyio


class Product(saffier.Model):
    id = saffier.IntegerField(primary_key=True)
    name = saffier.CharField(max_length=100)
    rating = saffier.IntegerField(minimum=1, maximum=5)
    in_stock = saffier.BooleanField(default=False)

    class Meta:
        registry = models
        name = "products"


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


async def test_queryset_delete():
    shirt = await Product.query.create(name="Shirt", rating=5)
    await Product.query.create(name="Belt", rating=5)
    await Product.query.create(name="Tie", rating=5)

    await Product.query.filter(pk=shirt.id).delete()
    assert await Product.query.count() == 2

    await Product.query.delete()
    assert await Product.query.count() == 0
