# Django Bulk Copy

Create your mass data in a faster way with the `COPY` command.
> Currently it supports only the Postgresql database.

### Install

`pip install django-bulk-copy`

### Usage

```python
class TestModel(models.Model):
    integer_field = models.IntegerField(null=True)
    char_field = models.CharField(max_length=32, null=True)
    boolean_field = models.BooleanField(default=False)
    datetime_field = models.DateTimeField(null=True)
    json_field = models.JSONField(null=True)
```

```python
from bulk_copy import BulkCopy

objects = [
    TestModel(
        integer_field=i,
        char_field=str(i),
        boolean_field=bool(i % 2),
        datetime_field=timezone.now(),
        json_field={i: f"{i:>09}"},
    )
    for i in range(1000)
]

BulkCopy(objects)
```

BulkCopy only uses the initial time of the transaction if your model has a date/datetime field with `auto_now=True`.

##### Additional
If you need to create your models from a csv file, [django-postgres-copy](https://palewi.re/docs/django-postgres-copy/) could be a better alternative.