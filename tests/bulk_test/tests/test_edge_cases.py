"""Edge case tests for bulk_copy functionality."""

from decimal import Decimal

import pytest

from ..models import Ahmet


class TestEmptyInput:
    """Tests for empty input handling."""

    @pytest.mark.django_db
    def test_empty_list_returns_none(self):
        assert Ahmet.objects.bulk_copy([]) is None

    @pytest.mark.django_db
    def test_empty_list_no_database_changes(self):
        initial_count = Ahmet.objects.count()
        Ahmet.objects.bulk_copy([])
        assert Ahmet.objects.count() == initial_count

    @pytest.mark.django_db
    def test_empty_generator(self):
        assert Ahmet.objects.bulk_copy(obj for obj in []) is None


class TestTypeValidation:
    """Tests for type validation."""

    @pytest.mark.django_db
    def test_wrong_model_type_raises_error(self, ahmet_factory, burak_factory):
        with pytest.raises(TypeError, match="Expected Ahmet, got Burak"):
            Ahmet.objects.bulk_copy([ahmet_factory(), burak_factory()])

    @pytest.mark.django_db
    def test_mixed_types_raises_error(self, ahmet_factory):
        with pytest.raises(TypeError, match="Expected Ahmet, got str"):
            Ahmet.objects.bulk_copy([ahmet_factory(), "not a model"])

    @pytest.mark.django_db
    def test_non_model_raises_error(self):
        with pytest.raises(TypeError, match="Expected Ahmet, got dict"):
            Ahmet.objects.bulk_copy([{"event": "test"}])


class TestBatchSize:
    """Tests for batch_size parameter."""

    @pytest.mark.django_db
    @pytest.mark.parametrize("batch_size", [0, -1, -100])
    def test_invalid_batch_size_raises_error(self, ahmet_factory, batch_size):
        with pytest.raises(ValueError, match="batch_size must be a positive integer"):
            Ahmet.objects.bulk_copy([ahmet_factory()], batch_size=batch_size)

    @pytest.mark.django_db
    @pytest.mark.parametrize("count,batch_size", [
        (5, 1),      # batch_size=1
        (3, 100),    # batch_size larger than list
        (10, 5),     # exact multiple
        (7, 3),      # with remainder
    ])
    def test_batch_size_variations(self, ahmet_factory, count, batch_size):
        objects = [ahmet_factory() for _ in range(count)]
        Ahmet.objects.bulk_copy(objects, batch_size=batch_size)
        assert Ahmet.objects.count() == count


class TestSpecialCharacters:
    """Tests for special character handling."""

    SPECIAL_STRINGS = [
        "Hello, World!",
        "Line1\nLine2",
        'Quote "test"',
        "Tab\there",
        "Backslash\\test",
        "Unicode: éèê",
        "SQL injection'; DROP TABLE--",
    ]

    SPECIAL_JSON = [
        {"key": "value with spaces"},
        {"key": 'quote "test"'},
        {"key": "newline\ntest"},
        {"nested": {"deep": "value"}},
        {"array": [1, 2, 3]},
        {"unicode": "éèê"},
        {"empty": ""},
        {"null_like": None},
    ]

    @pytest.mark.django_db
    @pytest.mark.parametrize("chars", SPECIAL_STRINGS)
    def test_special_chars_in_string_field(self, chars):
        obj = Ahmet(event=chars[:256], rate=Decimal("1.0"), data={})
        Ahmet.objects.bulk_copy([obj])
        assert Ahmet.objects.filter(event=chars[:256]).exists()

    @pytest.mark.django_db
    @pytest.mark.parametrize("data", SPECIAL_JSON)
    def test_special_chars_in_json_field(self, data):
        obj = Ahmet(event="test", rate=Decimal("1.0"), data=data)
        Ahmet.objects.bulk_copy([obj])
        assert Ahmet.objects.count() == 1


class TestNullValues:
    """Tests for null value handling."""

    @pytest.mark.django_db
    @pytest.mark.parametrize("data,expected", [
        (None, None),
        ({}, {}),
    ])
    def test_json_field_values(self, data, expected):
        obj = Ahmet(event="test", rate=Decimal("1.0"), data=data)
        Ahmet.objects.bulk_copy([obj])
        assert Ahmet.objects.first().data == expected

    @pytest.mark.django_db
    def test_empty_string_field(self):
        obj = Ahmet(event="", rate=Decimal("1.0"), data={})
        Ahmet.objects.bulk_copy([obj])
        assert Ahmet.objects.first().event == ""


class TestSingleObject:
    """Tests for single object handling."""

    @pytest.mark.django_db
    @pytest.mark.parametrize("batch_size", [None, 10])
    def test_single_object(self, ahmet_factory, batch_size):
        Ahmet.objects.bulk_copy([ahmet_factory()], batch_size=batch_size)
        assert Ahmet.objects.count() == 1


class TestLargeDataset:
    """Tests for large dataset handling."""

    @pytest.mark.django_db
    @pytest.mark.parametrize("batch_size", [None, 100])
    def test_thousand_objects(self, ahmet_factory, batch_size):
        objects = [ahmet_factory() for _ in range(1000)]
        Ahmet.objects.bulk_copy(objects, batch_size=batch_size)
        assert Ahmet.objects.count() == 1000


class TestGeneratorInput:
    """Tests for generator input handling."""

    @pytest.mark.django_db
    @pytest.mark.parametrize("batch_size", [None, 3])
    def test_generator_input(self, ahmet_factory, batch_size):
        Ahmet.objects.bulk_copy((ahmet_factory() for _ in range(10)), batch_size=batch_size)
        assert Ahmet.objects.count() == 10
