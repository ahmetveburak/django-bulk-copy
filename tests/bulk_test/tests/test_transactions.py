"""Transaction tests for bulk_copy functionality."""

from decimal import Decimal

import pytest
from django.db import IntegrityError, connection, transaction
from psycopg2.errors import UniqueViolation

from ..models import Ahmet


@pytest.mark.django_db(transaction=True)
class TestTransactionAtomicity:
    """Tests for transaction atomicity."""

    def test_operation_is_atomic(self, mocker, ahmet_factory):
        """Verify bulk_copy operations are wrapped in a transaction."""
        atomic_spy = mocker.spy(transaction, "atomic")

        Ahmet.objects.bulk_copy([ahmet_factory() for _ in range(5)])

        assert atomic_spy.call_count >= 1

    def test_failed_insert_rolls_back(self, ahmet_factory, unique_event_constraint):
        """Verify failed insert rolls back the entire operation."""
        Ahmet.objects.bulk_copy([ahmet_factory()])
        initial_count = Ahmet.objects.count()

        # Create objects with duplicate event (violates unique constraint)
        objects = [
            Ahmet(event="duplicate_event", rate=Decimal("1.0"), data={}),
            Ahmet(event="duplicate_event", rate=Decimal("2.0"), data={}),
        ]

        with pytest.raises((IntegrityError, UniqueViolation)):
            Ahmet.objects.bulk_copy(objects)

        assert Ahmet.objects.count() == initial_count

    def test_batch_failure_rolls_back_batch_only(self, unique_event_constraint):
        """Verify batch failures only roll back the failing batch."""
        initial_count = Ahmet.objects.count()

        # First batch - should succeed
        first_batch = [
            Ahmet(event=f"unique_event_{i}", rate=Decimal("1.0"), data={})
            for i in range(3)
        ]
        Ahmet.objects.bulk_copy(first_batch, batch_size=3)

        count_after_first = Ahmet.objects.count()
        assert count_after_first == initial_count + 3

        # Second batch with duplicates - should fail
        second_batch = [
            Ahmet(event="dup_event", rate=Decimal("1.0"), data={}),
            Ahmet(event="dup_event", rate=Decimal("2.0"), data={}),
        ]

        with pytest.raises((IntegrityError, UniqueViolation)):
            Ahmet.objects.bulk_copy(second_batch)

        # First batch should still be there
        assert Ahmet.objects.count() == count_after_first


@pytest.mark.django_db
class TestSequenceConsistency:
    """Tests for sequence consistency after operations."""

    def test_sequence_updated_after_insert(self, ahmet_factory, reset_ahmet_sequence):
        """Verify sequence is updated to correct value after insert."""
        sequence_name = reset_ahmet_sequence

        Ahmet.objects.bulk_copy([ahmet_factory() for _ in range(5)])

        max_pk = Ahmet.objects.order_by("-pk").first().pk

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT last_value FROM {sequence_name};")
            sequence_value = cursor.fetchone()[0]
            assert sequence_value >= max_pk

    def test_sequence_allows_next_insert(self, ahmet_factory):
        """Verify regular Django create works after bulk_copy."""
        Ahmet.objects.bulk_copy([ahmet_factory() for _ in range(5)])

        max_pk_after_bulk = Ahmet.objects.order_by("-pk").first().pk

        new_obj = Ahmet.objects.create(
            event="regular_create",
            rate=Decimal("1.0"),
            data={},
        )

        assert new_obj.pk > max_pk_after_bulk

    def test_multiple_bulk_copy_maintains_sequence(self, ahmet_factory):
        """Verify sequence is maintained across multiple bulk_copy calls."""
        Ahmet.objects.bulk_copy([ahmet_factory() for _ in range(3)])
        max_pk_1 = Ahmet.objects.order_by("-pk").first().pk

        Ahmet.objects.bulk_copy([ahmet_factory() for _ in range(3)])
        max_pk_2 = Ahmet.objects.order_by("-pk").first().pk

        assert max_pk_2 > max_pk_1
        assert Ahmet.objects.count() == 6


@pytest.mark.django_db(transaction=True)
class TestNestedTransactions:
    """Tests for nested transaction behavior."""

    def test_nested_in_outer_transaction(self, ahmet_factory):
        """Verify bulk_copy works within an outer transaction."""
        with transaction.atomic():
            Ahmet.objects.bulk_copy([ahmet_factory() for _ in range(5)])
            assert Ahmet.objects.count() == 5

        assert Ahmet.objects.count() == 5

    def test_outer_rollback_affects_bulk_copy(self, ahmet_factory):
        """Verify outer transaction rollback affects bulk_copy."""
        initial_count = Ahmet.objects.count()

        try:
            with transaction.atomic():
                Ahmet.objects.bulk_copy([ahmet_factory() for _ in range(5)])
                raise ValueError("Intentional rollback")
        except ValueError:
            pass

        assert Ahmet.objects.count() == initial_count
