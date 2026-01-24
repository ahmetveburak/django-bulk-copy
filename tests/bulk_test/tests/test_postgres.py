import csv
import sys

import pytest
from django.db import connection
from django.utils import timezone

from bulk_copy.engines.postgresql import PostgresCopy

from ..models import Ahmet


@pytest.mark.django_db
def test_is_called(ahmet_factory, reset_ahmet_sequence):
    """Verify sequence is_called flag is updated after bulk_copy."""
    sequence_table = reset_ahmet_sequence

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT last_value, is_called FROM {sequence_table};")
        sequence, is_called = cursor.fetchone()
        assert (sequence, is_called) == (1, False)

    # Create objects to invoke the sequence
    Ahmet.objects.bulk_copy([ahmet_factory()])
    Ahmet.objects.bulk_copy([ahmet_factory()])

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT last_value, is_called FROM {sequence_table};")
        sequence, is_called = cursor.fetchone()
        assert (sequence, is_called) == (2, True)


@pytest.mark.django_db
def test_csv_quoting_rule(mocker, ahmet_factory):
    """Verify correct CSV quoting based on Python version."""
    test_obj = ahmet_factory()

    mocker.patch("bulk_copy.engines.postgresql.sys.version_info", (3, 11))
    mock_csv_writer = mocker.patch("bulk_copy.engines.postgresql.csv.writer")
    Ahmet.objects.bulk_copy([test_obj])
    mock_csv_writer.assert_called_once_with(mocker.ANY, quoting=csv.QUOTE_MINIMAL)

    mock_quote_strings = mocker.patch("bulk_copy.engines.postgresql.csv.QUOTE_STRINGS", create=True)
    mocker.patch("bulk_copy.engines.postgresql.sys.version_info", (3, 12))
    Ahmet.objects.bulk_copy([test_obj])
    mock_csv_writer.assert_called_with(mocker.ANY, quoting=mock_quote_strings)


@pytest.mark.django_db
def test_copy_from_stream(mocker):
    """Verify CSV stream format for COPY command."""
    _tz_now = timezone.now()
    mocker.patch.object(timezone, "now", return_value=_tz_now)

    wrapper = PostgresCopy(model=Ahmet, using="default")
    wrapper._set_sequence_generator()  # Initialize the sequence

    temp_ahmet = Ahmet(
        version=1, event="", event_date=_tz_now, rate=1.1,
        data={"key": "value"}, is_active=True, created_at=_tz_now
    )

    # Directly test the stream building
    stream = wrapper._build_sql_stream([temp_ahmet])
    csv_string = stream.getvalue()

    expected_311 = f'1,,{_tz_now},1.1,"{{""key"": ""value""}}",True,{_tz_now}\r\n'
    expected_312 = f'1,"",{_tz_now},1.1,"{{""key"": ""value""}}",True,{_tz_now}\r\n'

    expected = expected_312 if sys.version_info >= (3, 12) else expected_311
    assert csv_string == expected
