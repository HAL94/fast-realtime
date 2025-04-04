from abc import ABC, abstractmethod
from typing import Any

from faker import Faker


class SeederBase(ABC):
    name: str

    def __init__(self, data: Any = None):
        self.fake = Faker()
        self.data = data
    
    @abstractmethod
    def _transform(self, data, *args, **kwargs):
        pass

    @abstractmethod
    def seed(self, *args, **kwargs):
        pass
    
