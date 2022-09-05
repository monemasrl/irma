class ObjectNotFoundException(Exception):
    """Exception raised when a database query returns no objects

    Attributes:
        object_type -- the object-type that has been queried
    """

    def __init__(self, obj):
        self.object_type = type(obj)
        super().__init__(
            f"Database query of object-type {self.object_type} returned no objects"
        )


class ObjectAttributeAlreadyUsedException(Exception):
    """Exception raised when attempting to create an object with an attribute
    that conflicts with an attribute with an object alreay in the db.

    Attributes:
        attribute -- the attrbiute that's already been used
    """

    def __init__(self, attribute):
        self.attribute = attribute
        super().__init__(
            f"Value '{attribute}' for field '{attribute.__name__}' is already"
        )
