import csv
import json
import sys
import uuid
from io import StringIO
from itertools import count
from typing import Generator, Sequence

from django.db import connections, models

from ..utils import uuid_generator
from .base import BaseCopyWrapper


class PostgresCopy(BaseCopyWrapper):
    def _get_sequence_generator(self) -> Generator[uuid.UUID, None, None] | count:
        if isinstance(self._model._meta.pk, models.UUIDField):
            return uuid_generator()

        connection = connections[self._using]
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_get_serial_sequence(%(table_name)s, %(pk_column)s);",
                {"table_name": self._model._meta.db_table, "pk_column": self._model._meta.pk.attname},
            )
            result = cursor.fetchone()
            if result is None or result[0] is None:
                raise ValueError(f"No sequence found for table '{self._model._meta.db_table}'")
            _sequence_table = result[0]

            cursor.execute(f"SELECT last_value, is_called FROM {_sequence_table}")
            _sequence, is_called = cursor.fetchone()
            if is_called:
                _sequence += 1

        return count(_sequence)

    def _update_table_sequence(self) -> None:
        if isinstance(self._model._meta.pk, models.UUIDField):
            return

        connection = connections[self._using]
        quoted_table = connection.ops.quote_name(self._model._meta.db_table)
        quoted_pk = connection.ops.quote_name(self._model._meta.pk.attname)

        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT setval(
                    pg_get_serial_sequence(%(table)s, %(pk)s),
                    COALESCE(max({quoted_pk}), 1),
                    max({quoted_pk}) IS NOT NULL
                ) FROM {quoted_table};
                """,
                {"table": self._model._meta.db_table, "pk": self._model._meta.pk.attname},
            )

    def _build_sql_stream(self, objs: Sequence[models.Model]) -> StringIO:
        csv_stream = StringIO()

        quoting = csv.QUOTE_STRINGS if sys.version_info >= (3, 12) else csv.QUOTE_MINIMAL  # type: ignore
        csv_writer = csv.writer(csv_stream, quoting=quoting)

        for obj in objs:
            obj_dict = obj.__dict__.copy()

            obj_dict[self._model._meta.pk.attname] = next(self._sequence)
            if _auto_fields := self._fields.auto_date_fields:
                obj_dict.update(_auto_fields)
            if _json_fields := self._fields.json_fields:
                obj_dict.update({json_field: json.dumps(obj_dict[json_field]) for json_field in _json_fields})

            csv_writer.writerow(self.field_getter(obj_dict))

        csv_stream.seek(0)
        return csv_stream

    def _build_copy_from_template(self) -> str:
        connection = connections[self._using]
        quoted_table = connection.ops.quote_name(self._model._meta.db_table)
        quoted_fields = ",".join(connection.ops.quote_name(f) for f in self._fields.field_names)

        return f"""
        COPY {quoted_table} ({quoted_fields})
        FROM STDIN
        WITH (
            FORMAT CSV,
            DELIMITER ',',
            NULL ''
        );
        """

    def _insert_objects(self, objs: Sequence[models.Model]) -> None:
        _sql = self._build_sql_stream(objs)
        _copy_from_sql = self._build_copy_from_template()

        with connections[self._using].cursor() as cursor:
            cursor.copy_expert(_copy_from_sql, _sql)
