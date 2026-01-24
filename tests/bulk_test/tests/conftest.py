"""Shared pytest fixtures for bulk_copy tests."""

from decimal import Decimal
from typing import Callable

import pytest
from django.db import connection

from ..models import Ahmet, Burak


@pytest.fixture
def ahmet_factory() -> Callable[..., Ahmet]:
    """Factory fixture for creating Ahmet instances."""
    from django.utils.crypto import get_random_string

    def _create(
        event: str | None = None,
        rate: Decimal | None = None,
        data: dict | None = None,
        **kwargs,
    ) -> Ahmet:
        return Ahmet(
            event=event or get_random_string(100),
            rate=rate or Decimal("1.23"),
            data=data if data is not None else {"key": get_random_string(20)},
            **kwargs,
        )

    return _create


@pytest.fixture
def burak_factory() -> Callable[..., Burak]:
    """Factory fixture for creating Burak instances."""
    from django.utils.crypto import get_random_string

    def _create(
        event: str | None = None,
        data: dict | None = None,
        is_active: bool = True,
        **kwargs,
    ) -> Burak:
        return Burak(
            event=event or get_random_string(100),
            data=data if data is not None else {},
            is_active=is_active,
            **kwargs,
        )

    return _create


@pytest.fixture
def reset_ahmet_sequence():
    """Reset Ahmet's primary key sequence to 1."""
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT pg_get_serial_sequence('{Ahmet._meta.db_table}', '{Ahmet._meta.pk.attname}');")
        sequence_name = cursor.fetchone()[0]
        cursor.execute(f"ALTER SEQUENCE {sequence_name} RESTART WITH 1;")

    yield sequence_name


@pytest.fixture
def mock_pg_connection(mocker):
    """Create a mock PostgreSQL connection for unit tests."""
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.side_effect = [
        ("mock_sequence_table",),  # sequence lookup
        (1, False),  # is_called check
    ]

    mock_conn = mocker.MagicMock()
    mock_conn.vendor = "postgresql"
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.ops.quote_name.side_effect = lambda x: f'"{x}"'

    return mock_conn, mock_cursor


@pytest.fixture
def unique_event_constraint():
    """Add and cleanup a unique constraint on event field."""
    constraint_name = "test_unique_event_fixture"

    with connection.cursor() as cursor:
        cursor.execute(f'ALTER TABLE "{Ahmet._meta.db_table}" ' f"ADD CONSTRAINT {constraint_name} UNIQUE (event);")

    yield constraint_name

    # Rollback any broken transaction before cleanup
    if connection.needs_rollback:
        connection.rollback()

    with connection.cursor() as cursor:
        cursor.execute(f'ALTER TABLE "{Ahmet._meta.db_table}" ' f"DROP CONSTRAINT IF EXISTS {constraint_name};")
