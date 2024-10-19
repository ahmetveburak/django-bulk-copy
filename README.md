# Django Bulk Copy 🚀
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![PyPI](https://img.shields.io/pypi/v/django-bulk-copy)
![Python](https://img.shields.io/badge/Support-Version%20%E2%89%A5%203.9-brightgreen)


<p>
  <img alt="Poetry" src="https://img.shields.io/badge/Poetry-60A5FA.svg?logo=Poetry&logoColor=white"/>
  <img alt="Black" src="https://img.shields.io/badge/code%20style-black-black"/>
  <img alt="Mypy" src="https://img.shields.io/badge/mypy-checked-blue"/>
  <img alt="isort" src="https://img.shields.io/badge/isort-checked-green"/>
  <img alt="bandit" src="https://img.shields.io/badge/security-bandit-yellow"/>
</p>

**⚠️ Only supports PostgreSQL**

## Install 🛠️

```
pip install django-bulk-copy
```

## Usage 🚀

```python
# models.py
from bulk_copy import BulkCopyManager
from django.db import models

class DummyModel(models.Model):
    integer_field = models.IntegerField(null=True)
    char_field = models.CharField(max_length=32, null=True)
    boolean_field = models.BooleanField(default=False)
    datetime_field = models.DateTimeField(null=True)
    json_field = models.JSONField(null=True)

    objects = BulkCopyManager()

# Usage
objects = [
    DummyModel(
        integer_field=i,
        char_field=str(i),
        boolean_field=bool(i % 2),
        datetime_field=timezone.now(),
        json_field={i: f"{i:>09}"},
    )
    for i in range(1000)
]

TestModel.objects.bulk_copy(objects)
```

> If your model has a date/datetime field with `auto_now=True`, `bulk_copy` will use the transaction's initial time instead of the object's creation.

### Benchmark 📊

| Object Count | `bulk_create` | `bulk_copy` |
| ------------ | ------------- |-------------|
| 1.000        | 0.06          | 0.05        |
| 10.000       | 0.34          | 0.08        |
| 100.000      | 3.96          | 0.80        |
| 1.000.000    | 38.96         | 7.57        |

### Additional Note 📝
If you need to create your models from a csv file, [django-postgres-copy](https://palewi.re/docs/django-postgres-copy/) could be a better alternative.
