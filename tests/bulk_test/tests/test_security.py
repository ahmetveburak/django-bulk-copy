"""Security tests for SQL injection prevention."""

import pytest
from django.db import connection

from bulk_copy.engines.postgresql import PostgresCopy

from ..models import Ahmet


@pytest.mark.django_db
class TestSQLInjectionPrevention:
    """Tests to verify SQL injection vectors are properly mitigated."""

    def test_quote_name_is_used_for_table_name(self, mocker):
        """Verify table names are quoted using connection.ops.quote_name."""
        mock_quote_name = mocker.spy(connection.ops, "quote_name")

        wrapper = PostgresCopy(model=Ahmet, using="default")
        wrapper._build_copy_from_template()

        call_args = [call[0][0] for call in mock_quote_name.call_args_list]
        assert Ahmet._meta.db_table in call_args

    def test_quote_name_is_used_for_field_names(self, mocker):
        """Verify field names are quoted using connection.ops.quote_name."""
        mock_quote_name = mocker.spy(connection.ops, "quote_name")

        wrapper = PostgresCopy(model=Ahmet, using="default")
        wrapper._build_copy_from_template()

        call_args = [call[0][0] for call in mock_quote_name.call_args_list]
        field_names = [f.attname for f in Ahmet._meta.fields]
        quoted_fields = [name for name in call_args if name in field_names]
        assert len(quoted_fields) == len(field_names)

    def test_parameterized_query_in_sequence_lookup(self, mocker, mock_pg_connection):
        """Verify sequence lookup uses parameterized queries."""
        mock_conn, mock_cursor = mock_pg_connection
        mocker.patch("bulk_copy.engines.postgresql.connections", {"default": mock_conn})

        wrapper = PostgresCopy(model=Ahmet, using="default")
        wrapper._get_sequence_generator()

        first_call = mock_cursor.execute.call_args_list[0]
        query = first_call[0][0]
        params = first_call[0][1] if len(first_call[0]) > 1 else first_call[1].get("params")

        assert "%(table_name)s" in query or "%(pk_column)s" in query
        assert params is not None

    def test_parameterized_query_in_sequence_update(self, mocker, mock_pg_connection):
        """Verify sequence update uses parameterized queries."""
        mock_conn, mock_cursor = mock_pg_connection
        mocker.patch("bulk_copy.engines.postgresql.connections", {"default": mock_conn})

        wrapper = PostgresCopy(model=Ahmet, using="default")
        wrapper._update_table_sequence()

        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("params")

        assert "%(table)s" in query or "%(pk)s" in query
        assert params is not None

    def test_copy_template_uses_quoted_identifiers(self):
        """Verify COPY template uses quoted identifiers."""
        wrapper = PostgresCopy(model=Ahmet, using="default")
        template = wrapper._build_copy_from_template()

        assert f'"{Ahmet._meta.db_table}"' in template
        assert f"COPY {Ahmet._meta.db_table} " not in template


@pytest.mark.django_db
class TestSequenceHandling:
    """Tests for sequence handling edge cases."""

    @pytest.mark.parametrize("fetchone_return", [
        (None,),  # sequence is None
        None,     # fetchone returns None
    ])
    def test_no_sequence_raises_error(self, mocker, fetchone_return):
        """Verify proper error when no sequence is found."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = fetchone_return

        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mocker.patch("bulk_copy.engines.postgresql.connections", {"default": mock_conn})

        wrapper = PostgresCopy(model=Ahmet, using="default")

        with pytest.raises(ValueError, match="No sequence found"):
            wrapper._get_sequence_generator()
