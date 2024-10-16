import pytest
from django.utils.crypto import get_random_string

from tests.bulk_test.models import Ahmet, Burak
from tests.bulk_test.tests.utils import create_ahmet


@pytest.mark.django_db
def test_bulk_copy_count():
    number_of_objects = 10
    objects = [create_ahmet() for _ in range(number_of_objects)]
    objects.extend([create_ahmet(include_defaults=True) for _ in range(number_of_objects)])
    Ahmet.objects.bulk_copy(objects)

    assert number_of_objects * 2 == Ahmet.objects.count()


@pytest.mark.django_db
def test_bulk_copy_uuid():
    number_of_objects = 10
    objects = [
        Burak(
            event=get_random_string(100),
            data={"knock": "knock"},
            is_active=bool(i % 3),
        )
        for i in range(number_of_objects)
    ]
    Burak.objects.bulk_copy(objects)

    assert number_of_objects == Burak.objects.count()


def test_unsupported_database(mocker):
    mocker.patch("bulk_copy.manager.settings.DATABASES", {"default": {"ENGINE": "django.db.backends.sqlite3"}})

    with pytest.raises(NotImplementedError, match="Database engine not supported."):
        Ahmet.objects.bulk_copy([])
