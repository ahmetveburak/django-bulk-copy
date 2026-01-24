from itertools import count
from typing import Generator, Sequence
from uuid import UUID

import pytest
from django.db import models

from bulk_copy.engines.base import BaseCopyWrapper

from ..models import Ahmet, Burak


class DummyCopy(BaseCopyWrapper):
    """Minimal implementation for testing BaseCopyWrapper."""

    def _update_table_sequence(self) -> None:
        pass

    def insert_objects(self, objs: Sequence[models.Model]) -> None:
        pass


@pytest.mark.django_db
class TestSequenceGenerator:
    """Tests for _get_sequence_generator method."""

    def test_integer_pk_returns_count(self):
        """Verify integer PK model returns count iterator."""
        wrapper = DummyCopy(model=Ahmet, using="default")
        sequence = wrapper._get_sequence_generator()

        assert isinstance(sequence, count)
        assert isinstance(next(sequence), int)

    def test_uuid_pk_returns_uuid_generator(self):
        """Verify UUID PK model returns UUID generator."""
        wrapper = DummyCopy(model=Burak, using="default")
        sequence = wrapper._get_sequence_generator()

        assert isinstance(sequence, Generator)
        assert isinstance(next(sequence), UUID)
