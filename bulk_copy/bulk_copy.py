import csv
import json
from io import StringIO
from operator import itemgetter
from typing import List, Sequence, TypeVar

from django.db import connections, models
from django.db.backends.postgresql.base import CursorDebugWrapper
from django.db.utils import DEFAULT_DB_ALIAS
from django.utils import timezone


class BulkCopy:
    def __init__(self, records_to_create: Sequence[models.Model]):
        self.model = self.get_model_class(records_to_create)
        self.meta = self.model._meta
        self.cursor = self.get_cursor()
        self.base_sql = self.generate_sql()
        self.auto_id_field = None
        self.bulk_copy(records_to_create)

    def get_model_class(self, records_to_create):
        if not records_to_create:
            raise ValueError(
                "At least one model instance is required to create data."
            )
        if not hasattr(records_to_create, "__getitem__"):
            raise TypeError("Objects must be subscriptable")

        return records_to_create[0].__class__

    @staticmethod
    def get_cursor(alias=DEFAULT_DB_ALIAS) -> CursorDebugWrapper:
        connection = connections[alias]
        connection.prepare_database()
        return connection.cursor()

    def generate_sql(self, delimiter=",", null=""):
        table_name = self.meta.db_table
        field_names = ",".join(
            f'"{field.name}_id"'
            if isinstance(field, models.ForeignKey)
            else f'"{field.name}"'
            for field in self.meta.fields
        )

        sql = f"""
        COPY "{table_name}" ({field_names})
        FROM STDIN 
        WITH (
            FORMAT CSV,
            DELIMITER '{delimiter}',
            NULL '{null}'
        );
        """
        return sql

    def model_to_io(self, records_to_create, is_auto_increment=True):
        output = StringIO()
        writer = csv.writer(
            output,
            delimiter=",",
            lineterminator="\n",
        )
        now = timezone.now().strftime("%Y-%m-%d %H:%M:%S.%s %z")
        fields = self.meta.fields

        last_pk = 0
        auto_id_key = None
        auto_now_keys = {}

        has_json_field = False
        json_fields = []

        field_names = []
        for i, field in enumerate(fields):
            if isinstance(field, models.AutoField):
                auto_id_key = self.auto_id_field = field.name
                last_pk = (
                    self.model.objects.aggregate(models.Max(field.name)).get(
                        f"{field.name}__max"
                    )
                    or last_pk
                )

            elif isinstance(field, models.DateField) and (
                field.auto_now or field.auto_now_add
            ):
                # save auto_now_add and auto_now field indexes
                # to set the now as default value
                auto_now_keys[field.name] = now
            elif isinstance(field, models.JSONField):
                has_json_field = True
                json_fields.append(field.name)

            if isinstance(field, models.ForeignKey):
                field_names.append(f"{field.name}_id")
            else:
                field_names.append(field.name)

        records = []
        for pk, record in enumerate(records_to_create, start=last_pk + 1):
            model_fields_dict = record.__dict__.copy()
            if is_auto_increment:
                model_fields_dict[auto_id_key] = pk
            if auto_now_keys:
                model_fields_dict.update(auto_now_keys)
            if has_json_field:
                model_fields_dict.update(
                    {
                        json_field: json.dumps(model_fields_dict[json_field])
                        for json_field in json_fields
                    }
                )

            model_fields = itemgetter(*field_names)(model_fields_dict)
            records.append(model_fields)
        writer.writerows(records)

        output.seek(0)
        return output

    def bulk_copy(self, records_to_create, is_auto_increment=True):
        data = self.model_to_io(records_to_create, is_auto_increment)
        self.cursor.copy_expert(self.base_sql, data)
        table_name = self.meta.db_table
        operation = f"""
        SELECT 
            setval(pg_get_serial_sequence('"{table_name}"','id'), max("{self.auto_id_field}"), max("{self.auto_id_field}") IS NOT null)
        FROM "{table_name}";
        """
        self.cursor.execute(operation)
