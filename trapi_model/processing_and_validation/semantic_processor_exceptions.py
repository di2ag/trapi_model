class UnsupportedCategoryAncestors(Exception):
    def __init__(self, category:str, message:str='Unsupported Category Ancestor') -> None:
        self.message = message
        #self.categories = [category.passed_name for category in categories]
        self.category = category
        super().__init__(message)

    def __str__(self) -> str:
        return '{}: {}'.format(self.message, self.category)

class UnsupportedPredicateAncestor(Exception):
    def __init__(self, predicate:str, message:str = 'Unsupported Predicate Ancestor') -> None:
        self.message = message
        self.predicate = predicate
        super().__init__(message)

    def __str__(self) -> str:
        return '{}: {}'.format(self.message, self.predicate)

class IndeterminableWildcardDescendent(Exception):
    def __init__(self, categories:list, message:str = 'Indeterminable Category Descendent') -> None:
        self.message = message
        self.categories = [category.passed_name for category in categories]
        super().__init__(message)
    
    def __str__(self) -> str:
        return '{}: {}'.format(self.message, self.categories)