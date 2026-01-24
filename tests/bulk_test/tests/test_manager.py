import pytest

from ..models import Ahmet, Burak


@pytest.mark.django_db
def test_bulk_copy_count(ahmet_factory):
    """Verify bulk_copy inserts correct number of objects."""
    objects = [ahmet_factory() for _ in range(10)]
    objects.extend([ahmet_factory(is_active=False) for _ in range(10)])
    Ahmet.objects.bulk_copy(objects)

    assert Ahmet.objects.count() == 20


@pytest.mark.django_db
def test_bulk_copy_uuid(burak_factory):
    """Verify bulk_copy works with UUID primary keys."""
    objects = [burak_factory(is_active=bool(i % 3)) for i in range(10)]
    Burak.objects.bulk_copy(objects)

    assert Burak.objects.count() == 10


def test_unsupported_database(mocker, ahmet_factory):
    """Verify NotImplementedError for unsupported database vendors."""
    mock_connection = mocker.MagicMock()
    mock_connection.vendor = "sqlite"
    mocker.patch("bulk_copy.manager.connections", {"default": mock_connection})

    with pytest.raises(NotImplementedError, match="Database vendor 'sqlite' is not supported."):
        Ahmet.objects.bulk_copy([ahmet_factory()])
