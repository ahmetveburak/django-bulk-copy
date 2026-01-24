# CLAUDE.md - AI Assistant Context

## Project Overview

django-bulk-copy provides 5-10x faster bulk inserts for Django/PostgreSQL using the COPY FROM command. It bypasses Django's ORM overhead by directly using PostgreSQL's efficient COPY protocol.

## Architecture

```
bulk_copy/
  __init__.py          # Exports BulkCopyManager
  manager.py           # User-facing API - BulkCopyManager
  utils.py             # UUID generator utility
  engines/
    base.py            # Abstract BaseCopyWrapper with field preparation
    postgresql.py      # PostgreSQL COPY implementation
```

## Data Flow

1. `Model.objects.bulk_copy(objects)` called
2. Manager validates input (type checking, empty list handling)
3. Manager selects PostgresCopy engine based on database vendor
4. Engine generates PKs from PostgreSQL sequence (or UUIDs for UUID fields)
5. Objects serialized to CSV format in StringIO buffer
6. `COPY FROM STDIN` executes bulk insert within a transaction
7. Sequence table updated to new max PK value

## Key Patterns

### SQL Safety
- **ALWAYS** use `connection.ops.quote_name()` for table/column identifiers
- **ALWAYS** use parameterized queries (`%(name)s` placeholders) for values
- **NEVER** use f-strings with user or database-derived values in SQL

### Transaction Safety
- All operations are wrapped in `transaction.atomic(using=self._using, savepoint=False)`
- Sequence reads, inserts, and sequence updates are atomic
- Failed inserts roll back completely

### Field Handling
- Auto-date fields (`auto_now`, `auto_now_add`) use transaction start time
- JSON fields are serialized with `json.dumps()`
- Primary keys are generated before insert using PostgreSQL sequences

## Commands

```bash
# Run tests with coverage
pytest tests/ --cov=bulk_copy --cov-report=term-missing

# Type checking
mypy bulk_copy

# Linting
ruff check bulk_copy tests

# Security scan
bandit -c pyproject.toml -r bulk_copy

# Start PostgreSQL for local development
docker run -d --name bulk_copy -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres -p 5432:5432 postgres

# Run migrations
DJANGO_SETTINGS_MODULE=tests.settings python manage.py migrate
```

## Important Gotchas

1. **Signals NOT fired**: Django's `pre_save` and `post_save` signals are NOT triggered
2. **auto_now timing**: Uses transaction start time, not per-object creation time
3. **PostgreSQL only**: Only PostgreSQL is supported (SQLite, MySQL not implemented)
4. **Multi-table inheritance**: Not supported
5. **Batch processing**: Use `batch_size` parameter for very large datasets to control memory
6. **Return value**: Returns `None` (objects are not updated with PKs in-place)

## Test Organization

```
tests/
  settings.py                    # Django settings for tests
  bulk_test/
    models.py                    # Test models (Ahmet, Burak)
    tests/
      test_manager.py            # Manager API tests
      test_postgres.py           # PostgreSQL-specific tests
      test_base.py               # Base wrapper tests
      test_security.py           # SQL injection prevention tests
      test_edge_cases.py         # Edge case and validation tests
      test_transactions.py       # Transaction behavior tests
```

## Common Development Tasks

### Adding a New Database Backend
1. Create new engine in `bulk_copy/engines/` (e.g., `mysql.py`)
2. Inherit from `BaseCopyWrapper`
3. Implement `_insert_objects()`, `_update_table_sequence()`, `_get_sequence_generator()`
4. Update `manager.py` to detect and use the new engine

### Adding Field Type Support
1. Update `_prepare_fields()` in `base.py` to detect the field type
2. Handle serialization in `_build_sql_stream()` in the engine
3. Add tests for the new field type
