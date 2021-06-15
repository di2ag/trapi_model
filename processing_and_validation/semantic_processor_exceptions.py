from trapi_model.biolink import BiolinkEntity

class UnsupportedCategoryAncestors(Exception):
    def __init__(self, categories:list, message:str='Unsupported Category Ancestor') -> None:
        self.message = message
        self.categories = [passed_name for category.passed_name in categories]

        super().__init__(message)

    def __str__(self) -> str:
        return '{}: {}'.format(self.message, self.categories)

class UnsupportedPredicateAncestor(Exception):
    def __init__(self, predicates:list, message:str = 'Unsupported Predicate Ancestor') -> None:
        self.message = message
        self.predicate = [passed_name for predicate.passed_name in predicates]
        super().__init__(message)

    def __str__(self) -> str:
        return '{}: {}'.format(self.message, self.predicate)

class IndeterminableCategoryDescendent(Exception):
    def __init__(self, categories:list, message:str = 'Indeterminable Category Descendent') -> None:
        self.message = message
        self.categories = [passed_name for categories.passed_name in categories]
        super().__init__(message)
    
    def __str__(self) -> str:
        return '{}: {}'.format(self.message, self.categories)