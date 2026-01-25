"""Compatibility layer for psycopg2 and psycopg3."""

from io import StringIO

# Detect which psycopg version is available
PSYCOPG_VERSION: int | None = None

try:
    import psycopg  # type: ignore[import-not-found]  # noqa: F401

    PSYCOPG_VERSION = 3
except ImportError:
    try:
        import psycopg2  # type: ignore[import-untyped]  # noqa: F401

        PSYCOPG_VERSION = 2
    except ImportError:
        pass


def copy_from_stream(cursor, sql: str, stream: StringIO) -> None:
    """Execute COPY FROM STDIN with compatibility for psycopg2 and psycopg3.

    Args:
        cursor: Django database cursor (CursorWrapper)
        sql: COPY FROM STDIN SQL statement
        stream: StringIO containing CSV data
    """
    # Access the raw psycopg cursor from Django's wrapper
    raw_cursor = getattr(cursor, "cursor", cursor)

    if PSYCOPG_VERSION == 3:
        with raw_cursor.copy(sql) as copy:
            copy.write(stream.read())
    elif PSYCOPG_VERSION == 2:
        raw_cursor.copy_expert(sql, stream)
    else:
        raise ImportError("Neither psycopg nor psycopg2 is installed")
