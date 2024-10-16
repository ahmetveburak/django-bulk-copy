from django.db import models

from bulk_copy.manager import BulkCopyManager


class Ahmet(models.Model):
    version = models.BigAutoField(primary_key=True)
    event = models.CharField(max_length=256)
    event_date = models.DateField(auto_now=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BulkCopyManager()


class Burak(models.Model):
    version = models.UUIDField(primary_key=True)
    event = models.CharField(max_length=256)
    data = models.JSONField()
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey(Ahmet, null=True, on_delete=models.CASCADE, related_name="buraks")

    objects = BulkCopyManager()
