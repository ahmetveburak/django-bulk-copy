from bulk_copy import BulkCopy
from django.test import TestCase
from django.utils import timezone

from tests.bulk_test.models import TestModel


class BulkCopyTests(TestCase):
    def test_bulk_copy_no_data(self):
        self.assertRaises(ValueError, BulkCopy, [])

    def test_bulk_copy_generator(self):
        number_of_objects = 10
        objects = (
            TestModel(
                integer_field=i,
                char_field=str(i),
                boolean_field=bool(i % 3),
                json_field={i: f"{i:>05}"},
                datetime_field=timezone.now(),
            )
            for i in range(number_of_objects)
        )
        self.assertRaises(TypeError, BulkCopy, objects)

    def test_bulk_copy_count(self):
        number_of_objects = 10
        objects = [
            TestModel(
                integer_field=i,
                char_field=str(i),
                boolean_field=bool(i % 3),
                json_field={i: f"{i:>05}"},
                datetime_field=timezone.now(),
            )
            for i in range(number_of_objects)
        ]
        BulkCopy(objects)

        self.assertEqual(number_of_objects, TestModel.objects.count())
