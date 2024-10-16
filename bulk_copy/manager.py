from typing import Sequence

from django.conf import settings
from django.db import models

from .engines.base import BaseCopyWrapper
from .engines.postgresql import PostgresCopy


class BulkCopyManager(models.Manager):
    def bulk_copy(self, objs: Sequence[models.Model]) -> None:
        _copy_wrapper = self._get_copy_wrapper()
        return _copy_wrapper.insert_objects(objs)

    def _get_copy_wrapper(self) -> BaseCopyWrapper:
        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
            return PostgresCopy(model=self.model, using=self.db)  # type: ignore
        else:
            raise NotImplementedError("Database engine not supported.")
