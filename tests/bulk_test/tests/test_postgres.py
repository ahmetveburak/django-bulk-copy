import pytest
from django.db import connection

from ..models import Ahmet
from .utils import create_ahmet


@pytest.mark.django_db
def test_is_called():
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT pg_get_serial_sequence('{Ahmet._meta.db_table}', '{Ahmet._meta.pk.attname}');")
        sequence_table = cursor.fetchone()[0]

        cursor.execute(f"ALTER SEQUENCE {sequence_table} RESTART WITH 1;")

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT last_value, is_called FROM {sequence_table};")
        sequence, is_called = cursor.fetchone()
        assert (sequence, is_called) == (1, False)

    # Create an object to invoke the sequence
    Ahmet.objects.bulk_copy([create_ahmet()])
    # `is_called` should be true
    Ahmet.objects.bulk_copy([create_ahmet()])

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT last_value, is_called FROM {sequence_table};")
        sequence, is_called = cursor.fetchone()
        assert (sequence, is_called) == (2, True)
