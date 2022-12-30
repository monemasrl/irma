from beanie import Document, PydanticObjectId
from beanie.exceptions import DocumentWasNotSaved


class CustomDocument(Document):
    @property
    def id(self) -> PydanticObjectId:
        obj_id = super().id
        if obj_id is None:
            raise DocumentWasNotSaved

        return obj_id
