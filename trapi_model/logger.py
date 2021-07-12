import datetime

from trapi_model.base import TrapiBaseClass

class LogEntry(TrapiBaseClass):
    def __init__(self, level, message, code=None):
        self.time = datetime.datetime.utcnow().isoformat()
        self.level = level
        self.message = message
        self.code = code

    def to_dict(self):
        return {
                "timestamp": self.time,
                "level": self.level,
                "message": self.message,
                "code": self.code,
                }

class Logger(TrapiBaseClass):
    def __init__(self):
        self.logs = []

    def add_log(self, level, message, code=None):
        self.logs.append(
                LogEntry(
                    level,
                    message,
                    code,
                    )
                )

    def info(self, message, code=None):
        self.add_log(INFO, message, code)

    def debug(self, message, code=None):
        self.add_log(DEBUG, message, code)

    def warning(self, message, code=None):
        self.add_log(WARNING, message, code)

    def error(self, message, code=None):
        self.add_log(ERROR, message, code)

    def to_dict(self):
        logs = [log.to_dict() for log in self.logs]
        return logs 
