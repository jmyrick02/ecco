from typing import Optional, List, Callable
from abc import ABC, abstractmethod

# https://en.wikipedia.org/wiki/Fowler%E2%80%93Noll%E2%80%93Vo_hash_function#FNV_offset_basis
FNV_OFFSET_BASIS = 0xCBF29CE484222325
# Just some big prime number
FNV_PRIME = 0x100000001B3


class SymbolTableEntry:
    def __init__(self, _identifier_name: str, _value: int):
        self.identifier_name: str = _identifier_name
        self.value: int = _value

        self.next: Optional[SymbolTableEntry] = None


class SymbolTableInterface(ABC):
    def __init__(self, length: int = 512):
        pass

    @property
    @abstractmethod
    def length(self):
        pass

    @abstractmethod
    def update(
        self,
        identifier: str,
        entry: Optional[SymbolTableEntry],
    ) -> bool:
        pass

    @abstractmethod
    def get(self, identifier: str) -> Optional[SymbolTableEntry]:
        pass

    # These three methods are going to let us access SymbolTableEntries via a
    # list access operator, like symbol_table["x"]

    def __delitem__(self, key: str) -> None:
        self.update(key, None)

    def __getitem__(self, key: str) -> Optional[SymbolTableEntry]:
        return self.get(key)

    def __setitem__(self, key: str, value: Optional[SymbolTableEntry]):
        self.update(key, value)


class HashTableSymbolTable(SymbolTableInterface):
    def __init__(self, length: int = 512):
        self.data: List[Optional[SymbolTableEntry]] = [None] * length

    @property
    def length(self) -> int:
        """Length of symbol table"""
        return len(self.data)

    def resize(self, factor: int = 2) -> None:
        """Resizes symbol table by a factor of factor

        Args:
            factor (int, optional): Factor by which to expand symbol table. Defaults to 2.
        """
        self.data += [None] * factor

    def update(self, identifier: str, entry: Optional[SymbolTableEntry]) -> bool:
        """Assign a new value to an identifier

        Args:
            identifier (str): Identifier to assign to
            entry (Optional[SymbolTableEntry]): Value to assign

        Returns:
            bool: If the symbol already existed in the table
        """
        id_index = self.hash(identifier)

        symbol_already_exists = False

        if self.data[id_index] is None:
            symbol_already_exists = True

        self.data[id_index] = entry

        return symbol_already_exists

    def get(self, identifier: str) -> Optional[SymbolTableEntry]:
        """Get a value from the symbol table

        Args:
            identifier (str): Identifier mapped to output value

        Returns:
            Optional[SymbolTableEntry]: Value mapped from provided identifier
        """
        return self.data[self.hash(identifier)]

    def hash(self, s: str) -> int:
        """Hash function converting identifiers to hash table indices

        Args:
            s (str): String to hash

        Returns:
            int: FNV-1 value of input string
        """
        # Implementation of FNV_1A
        # Check out this post for other hashes you could implement
        # https://softwareengineering.stackexchange.com/questions/49550/which-hashing-algorithm-is-best-for-uniqueness-and-speed

        hash: int = FNV_OFFSET_BASIS

        for c in s:
            hash ^= ord(c)
            hash *= FNV_PRIME

        return hash % self.length


class FPSymbolTable(SymbolTableInterface):
    def __init__(self, length: int = 0):
        self.data: Callable[[str], Optional[SymbolTableEntry]] = self.identity_table

        self._length: int = 0

    @staticmethod
    def identity_table(s: str) -> Optional[SymbolTableEntry]:
        return None

    @property
    def length(self) -> int:
        return self._length

    def update(self, identifier: str, entry: Optional[SymbolTableEntry]) -> bool:
        symbol_already_exists: bool = self.get(identifier) is not None

        def new_symbol_table(s: str) -> Optional[SymbolTableEntry]:
            current_symbol_table = self.data

            if s == identifier:
                return entry

            return current_symbol_table(s)

        self.data = new_symbol_table

        if not symbol_already_exists and entry is not None:
            self._length += 1
        elif symbol_already_exists and entry is None:
            self._length -= 1

        return symbol_already_exists

    def get(self, identifier: str) -> Optional[SymbolTableEntry]:
        return self.data(identifier)


SymbolTable = HashTableSymbolTable