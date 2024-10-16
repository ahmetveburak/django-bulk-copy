from uuid import UUID

from bulk_copy import utils


def test_uuid_generator():
    _uuid = next(utils.uuid_generator())
    assert isinstance(_uuid, UUID)
