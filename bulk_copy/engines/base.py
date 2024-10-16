from abc import ABC, abstractmethod
from datetime import datetime
from functools import cached_property
from itertools import count
from operator import itemgetter
from typing import Any, Generator, NamedTuple, Sequence
from uuid import UUID

from django.db import models
from django.utils import timezone

from ..utils import uuid_generator


class FieldRepo(NamedTuple):
    field_names: Sequence[str]
    auto_date_fields: dict[str, datetime]
    json_fields: Sequence[str]


class BaseCopyWrapper(ABC):
    def __init__(self, model: models.Model, using: str):
        self._model = model
        self._using = using
        self._fields = self._prepare_fields()
        self._sequence: Generator[UUID, None, None] | count[Any]

    @cached_property
    def field_getter(self) -> itemgetter:
        return itemgetter(*self._fields.field_names)

    def _prepare_fields(self) -> FieldRepo:
        field_names = []
        auto_date_fields = {}
        json_fields = []

        _tz_now = timezone.now()

        field: models.Field
        for field in self._model._meta.fields:
            if isinstance(field, models.DateField) and (field.auto_now or field.auto_now_add):
                auto_date_fields[field.attname] = _tz_now
            elif isinstance(field, models.JSONField):
                json_fields.append(field.attname)

            field_names.append(field.attname)

        return FieldRepo(field_names, auto_date_fields, json_fields)

    def _get_sequence_generator(self) -> Generator[UUID, None, None] | count:
        if isinstance(self._model._meta.pk, models.UUIDField):
            return uuid_generator()

        max_pk = self._model.objects.aggregate(models.Max("pk")).get("pk__max") or 0  # type: ignore
        return count(max_pk + 1)

    def insert_objects(self, objs: Sequence[models.Model]) -> None:
        self._set_sequence_generator()
        self._insert_objects(objs)
        self._update_table_sequence()

    def _set_sequence_generator(self) -> None:
        self._sequence = self._get_sequence_generator()

    @abstractmethod
    def _update_table_sequence(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _insert_objects(self, objs: Sequence[models.Model]) -> None:
        raise NotImplementedError
