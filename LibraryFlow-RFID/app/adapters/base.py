from abc import ABC, abstractmethod
from typing import Any

class DeviceAdapter(ABC):
    """Vendor-neutral seam; replace mock implementation with authorised vendor SDK/API."""
    @abstractmethod
    def health(self) -> dict[str, Any]: ...

class IlmsAdapter(ABC):
    """An anti-corruption boundary: never write into a live ILMS without a reviewed contract."""
    @abstractmethod
    def checkout(self, accession_no: str, member_no: str) -> dict[str, Any]: ...
