class UnprocessableResponseException(Exception):
    def __init__(
            self, message: dict
    ) -> None:
        self.message = message

    def __str__(self):
        return f"Unprocessable response: {self.message}"


class RepositoryException(Exception):
    pass
