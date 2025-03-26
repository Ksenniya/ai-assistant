class ChatNotFoundException(Exception):
    def __init__(self, message="Chat not found"):
        self.message = message
        self.status_code = 404
        super().__init__(self.message)

class InvalidTokenException(Exception):
    def __init__(self, message="Invalid token"):
        self.message = message
        self.status_code = 401
        super().__init__(self.message)

class RequestLimitExceededException(Exception):
    def __init__(self, message="Request limit exceeded"):
        self.message = message
        self.status_code = 429
        super().__init__(self.message)