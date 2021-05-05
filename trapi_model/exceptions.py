""" Custom TRAPI Model Exceptions.
"""

class UnsupportedTrapiVersion(Exception):
    def __init__(self, version, message='Trapi Version not supported'):
        self.version = version
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return '{}: {}'.format(self.message, self.version)

class UnsupportedBiolinkVersion(Exception):
    def __init__(self, version, message='Biolink Version not supported'):
        self.version = version
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return '{}: {}'.format(self.message, self.version)

class InvalidTrapiComponent(Exception):
    def __init__(self, trapi_version, trapi_component, validation_error_msg, message='Invalid TRAPI Component'):
        self.trapi_version = trapi_version
        self.trapi_component = trapi_component
        self.validation_error_msg = validation_error_msg
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return '{}: {} in Schema v{}, exited with {}'.format(
                self.message,
                self.trapi_component,
                self.trapi_version,
                self.validation_error_msg
                )

class UnknownBiolinkEntity(Exception):
    def __init__(self, name, message='Unknown Biolink Entity'):
        self.name = name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return '{}: {}'.format(
                self.message,
                self.name,
                )
