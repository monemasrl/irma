from typing import TypeVar

from beanie import Document, Link

from ...utils.exceptions import NotFoundException

T = TypeVar("T", bound=Document)


async def fetch_or_raise(link: Link[T]) -> T:
    resolved = await link.fetch()

    if isinstance(resolved, Link):
        raise NotFoundException(T.__name__)

    return resolved
