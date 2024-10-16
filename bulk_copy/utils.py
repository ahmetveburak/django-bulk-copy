import typing
import uuid


def uuid_generator() -> typing.Generator[uuid.UUID, None, None]:
    while True:
        yield uuid.uuid4()
