import csv
from io import StringIO
from operator import itemgetter

from django.db import connections, models
from django.db.backends.postgresql.base import CursorDebugWrapper
from django.db.utils import DEFAULT_DB_ALIAS
from django.utils import timezone


class BulkCopy:
    def __init__(self, model, records_to_create):
        self.model = model
        self.meta = model._meta
        self.cursor = self.get_cursor()
        self.base_sql = self.generate_sql()
        self.auto_id_field = None
        self.bulk_copy(records_to_create)

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

            if isinstance(field, models.ForeignKey):
                field_names.append(f"{field.name}_id")
            else:
                field_names.append(field.name)

        records = []
        for pk, record in enumerate(records_to_create, start=last_pk + 1):
            model_fields_dict = record.__dict__
            if is_auto_increment:
                model_fields_dict[auto_id_key] = pk
            if auto_now_keys:
                model_fields_dict.update(auto_now_keys)
            model_fields = itemgetter(*field_names)(model_fields_dict)
            records.append(model_fields)
        writer.writerows(records)

        output.seek(0)
        return output

    def bulk_copy(
        self, records_to_create, is_auto_increment=True, update_sequence=False
    ):
        data = self.model_to_io(records_to_create, is_auto_increment)
        self.cursor.copy_expert(self.base_sql, data)
        if update_sequence:
            # TODO update sequence number after data inserted
            ...
        table_name = self.meta.db_table
        operation = f"""
        SELECT 
            setval(pg_get_serial_sequence('"{table_name}"','id'), 1, max(f"{self.auto_id_field}") IS NOT null)
        FROM "{table_name}";
        """
