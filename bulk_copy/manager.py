from typing import Sequence

from django.db import connections, models

from .engines.base import BaseCopyWrapper
from .engines.postgresql import PostgresCopy


class BulkCopyManager(models.Manager):
    def bulk_copy(self, objs: Sequence[models.Model], batch_size: int | None = None) -> None:
        """
        Insert objects using PostgreSQL COPY command for better performance.

        Args:
            objs: Sequence of model instances to insert.
            batch_size: Optional batch size for processing large datasets.
                       If None, all objects are inserted in a single operation.

        Raises:
            TypeError: If any object is not an instance of the manager's model.
            ValueError: If batch_size is not a positive integer.

        Note:
            Django signals (pre_save, post_save) are NOT fired.
            auto_now fields use the transaction start time, not per-object time.
        """
        if batch_size is not None and batch_size <= 0:
            raise ValueError("batch_size must be a positive integer.")

        if not objs:
            return None

        objs_list = list(objs)
        for obj in objs_list:
            if not isinstance(obj, self.model):
                raise TypeError(f"Expected {self.model.__name__}, got {type(obj).__name__}")

        _copy_wrapper = self._get_copy_wrapper()

        if batch_size is None:
            _copy_wrapper.insert_objects(objs_list)
        else:
            for i in range(0, len(objs_list), batch_size):
                batch = objs_list[i : i + batch_size]
                _copy_wrapper.insert_objects(batch)

        return None

    def _get_copy_wrapper(self) -> BaseCopyWrapper:
        connection = connections[self.db]
        if connection.vendor == "postgresql":
            return PostgresCopy(model=self.model, using=self.db)  # type: ignore
        raise NotImplementedError(f"Database vendor '{connection.vendor}' is not supported.")
