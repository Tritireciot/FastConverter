from typing import Type
from pydantic import BaseModel


class UnprocessableResponseException(Exception):
    def __init__(
        self, message: dict, validation_type: Type[BaseModel], destination: str
    ) -> None:
        self.message = message
        self.validation_type = validation_type
        self.destination = destination

    def __str__(self):
        return f"Unprocessable response: {self.message} for model: {self.validation_type}"


class RepositoryException(Exception):
    pass