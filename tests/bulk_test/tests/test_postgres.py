import csv
import sys
from io import StringIO

import pytest
import pytest_mock
from django.db import connection, connections
from django.utils import timezone

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


@pytest.mark.django_db
def test_csv_quoting_rule(mocker: pytest_mock.MockFixture):
    mocker.patch("bulk_copy.engines.postgresql.sys.version_info", (3, 11))
    mock_csv_writer = mocker.patch("bulk_copy.engines.postgresql.csv.writer")
    Ahmet.objects.bulk_copy([])
    mock_csv_writer.assert_called_once_with(mocker.ANY, quoting=csv.QUOTE_MINIMAL)

    mock_quote_strings = mocker.patch("bulk_copy.engines.postgresql.csv.QUOTE_STRINGS", create=True)
    mocker.patch("bulk_copy.engines.postgresql.sys.version_info", (3, 12))
    Ahmet.objects.bulk_copy([])
    mock_csv_writer.assert_called_with(mocker.ANY, quoting=mock_quote_strings)


#
@pytest.mark.django_db
def test_copy_from_stream(mocker: pytest_mock.MockFixture):
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.side_effect = [
        ("mock_sequence_table",),  # First fetchone call
        (1, False),  # Second fetchone call
    ]
    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    connections["default"] = mock_connection

    _tz_now = timezone.now()
    mocker.patch.object(timezone, "now", return_value=_tz_now)

    temp_ahmet = Ahmet(
        version=1, event="", event_date=_tz_now, rate=1.1, data={"key": "value"}, is_active=True, created_at=_tz_now
    )

    expected_result = f'1,,{_tz_now},1.1,"{{""key"": ""value""}}",True,{_tz_now}\r\n'
    # After 3.12, empty strings are quoted if quoting is set to QUOTE_STRINGS
    expected_result_312 = f'1,"",{_tz_now},1.1,"{{""key"": ""value""}}",True,{_tz_now}\r\n'

    Ahmet.objects.bulk_copy([temp_ahmet])
    stream: StringIO = mock_cursor.copy_expert.call_args[0][1]
    csv_string = stream.read()

    if sys.version_info >= (3, 12):
        assert csv_string == expected_result_312
    else:
        assert csv_string == expected_result
