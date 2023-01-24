# Django Bulk Copy 🚀
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ahmetveburak/django-bulk-copy/main.svg)](https://results.pre-commit.ci/latest/github/ahmetveburak/django-bulk-copy/main)
![GitHub contributors](https://img.shields.io/github/contributors/ahmetveburak/django-bulk-copy)


![PyPI](https://img.shields.io/pypi/v/django-bulk-copy)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-bulk-copy)
![PyPI - Downloads](https://img.shields.io/pypi/dm/django-bulk-copy?color=red)
![PyPI - Format](https://img.shields.io/pypi/format/django-bulk-copy)
![PyPI - Status](https://img.shields.io/pypi/status/django-bulk-copy?color=orange)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/django-bulk-copy)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/django-bulk-copy)


<p>
  <img alt="Poetry" src="https://img.shields.io/badge/Poetry-60A5FA.svg?logo=Poetry&logoColor=white"/>
  <img alt="Black" src="https://img.shields.io/badge/code%20style-black-black"/>
  <img alt="Mypy" src="https://img.shields.io/badge/mypy-checked-blue"/>
  <img alt="isort" src="https://img.shields.io/badge/isort-checked-green"/>
  <img alt="bandit" src="https://img.shields.io/badge/security-bandit-yellow"/>
</p>

**Create your mass data in a faster way with the** `COPY` **command**.

**⚠️ Currently it supports only the Postgresql database. ⚠️**

## Install 🛠️

```
pip install django-bulk-copy
```

## Usage 🚀

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

### Benchmark 📊

| Object Count | `bulk_create` | `BulkCopy` |
| ------------ | ------------- | ---------- |
| 1.000        | 0.06          | 0.05       |
| 10.000       | 0.34          | 0.08       |
| 100.000      | 3.96          | 0.80       |
| 1.000.000    | 38.96         | 7.57       |

### Additional Note 📝
If you need to create your models from a csv file, [django-postgres-copy](https://palewi.re/docs/django-postgres-copy/) could be a better alternative.
