import random
from datetime import datetime
from decimal import Decimal

from django.utils.crypto import get_random_string

from tests.bulk_test.models import Ahmet


def create_ahmet(include_defaults: bool = False) -> Ahmet:
    data = {
        "event": get_random_string(100),
        "rate": Decimal("1.23"),
        "data": {get_random_string(20): get_random_string(30)},
    }

    if include_defaults:
        random_date = datetime.fromtimestamp(random.randint(1_000_000_000, 2_000_000_000))
        data.update(
            {
                "event_date": random_date.date(),
                "created_at": random_date,
                "is_active": bool(random_date.timestamp() % 3),
            }
        )

    return Ahmet(**data)
