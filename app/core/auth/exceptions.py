class InvalidTokenError(Exception):
    def __init__(self, message: str = 'Token invalid'):
        super().__init__(message)
        self.message = message