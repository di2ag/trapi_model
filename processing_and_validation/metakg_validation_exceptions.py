class UnsupportedNodeEdgeRelationship(Exception):
    def __init__(self, biolink_entity_subject:str,  biolink_predicate:str, biolink_entity_object:str, message:str='Unsupported Relationship') -> None:
        self.biolink_entity_subject = biolink_entity_subject
        self.biolink_entity_object = biolink_entity_object
        self.biolink_predicate = biolink_predicate
        self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return '{}: {} -> {} -> {}'.format(
            self.message,
            self.biolink_entity_subject,
            self.biolink_predicate,
            self.biolink_entity_object
        )

class UnsupportedPredicate(Exception):
    def __init__(self, predicate:str, message:str='Unsupported Predicate') -> None:
        self.message = message
        self.predicate = predicate
        super().__init__(self.message)

    def __str__(self) -> str:
        return '{}: {}'.format(self.message, self.predicate)

class UnsupportedCategory(Exception):
    def __init__(self, entity:str, message:str='Unsupported Entity') -> None:
        self.message = message
        self.entity = entity
        super().__init__(self.message)

    def __str__(self) -> str:
        return '{}: {}'.format(self.message)

class UnsupportedPrefix(Exception):
    def __init__(self, prefix:str, message:str='Unsupported Prefix') -> None:
        self.message = message
        self.prefix = prefix
        super().__init__(self.message)

    def __str__(self) -> str:
        return '{}: {}'.format(self.message, self.prefix)

class UnsupportedPrefixCategoryPair(Exception):
    def __init__(self, entity:str, prefix:str, message:str = 'Unsupported Prefix Category Pair') -> None:
        self.entity = entity
        self.prefix = prefix
        self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return '{}: {} -> {}'.format(self.message, self.prefix, self.entity)