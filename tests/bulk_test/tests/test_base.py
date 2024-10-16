from itertools import count
from typing import Generator, Sequence
from uuid import UUID

import pytest
import pytest_mock
from django.db import models

from bulk_copy.engines.base import BaseCopyWrapper
from tests.bulk_test.models import Ahmet, Burak


class DummyCopy(BaseCopyWrapper):
    def _update_table_sequence(self) -> None:
        pass

    def _insert_objects(self, objs: Sequence[models.Model]) -> None:
        pass


@pytest.mark.django_db
def test_get_sequence_generator(mocker: pytest_mock.MockFixture):
    copy_wrapper = DummyCopy(model=Ahmet, using="default")
    sequence = copy_wrapper._get_sequence_generator()
    assert isinstance(sequence, count)
    assert isinstance(next(sequence), int)

    copy_wrapper = DummyCopy(model=Burak, using="default")
    sequence = copy_wrapper._get_sequence_generator()
    assert isinstance(sequence, Generator)
    assert isinstance(next(sequence), UUID)
