from abc import ABC, abstractmethod


class BaseDocumentLoader(ABC):
    @abstractmethod
    def load(self, raw_bytes: bytes) -> str:
        """
        Recebe bytes do arquivo e retorna texto extraído.
        """
        pass
