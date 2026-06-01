from abc import ABC, abstractmethod


class DocumentLoader(ABC):
    @abstractmethod
    def load(self, bucket: str, key: str):
        pass
