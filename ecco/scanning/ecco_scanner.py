import os
from typing import TextIO

from ..utils.ecco_logging import EccoFileNotFound, EccoSyntaxError, EccoIdentifierError
from .ecco_token import Token, TokenType


class Scanner:
    def __init__(self, input_fn: str):
        """A class for scanning in Tokens

        Args:
            input_fn (str): Filename of the input program file
        """
        self.filename: str = input_fn
        self.file: TextIO

        self.put_back_buffer: str = ""

        self.line_number: int = 1
        self.char_number: int = 1

        self.current_token: Token

        self.initialized: bool = False

    def __enter__(self):
        """Opens the program file for scanning

        Raises:
            EccoFileNotFound: If the program file does not exist
        """
        if os.path.exists(self.filename):
            self.file = open(self.filename, "r")
        else:
            raise EccoFileNotFound(self.filename)

        self.initialized = True

        return self

    def __exit__(self, _, __, ___):
        """Closes the program file"""
        if not self.file.closed:
            self.file.close()

    def open(self):
        """Opens the program file for scanning

        Raises:
            EccoFileNotFound: If the program file does not exist
        """
        self.__enter__()

    def close(self):
        """Closes the program file"""
        self.__exit__(None, None, None)

    def next_character(self) -> str:
        """Get the next character from the input stream

        Returns:
            str: The next character from the input stream
        """
        c: str = ""

        # If we have a character in the putback buffer,
        # we want to read that first, then empty the
        # buffer
        if self.put_back_buffer:
            c = self.put_back_buffer
            self.put_back_buffer = ""
            return c

        # Otherwise, we read a single character from
        # the open input file, and conditionally
        # increment our rudimentary line counter
        c = self.file.read(1)
        self.char_number += 1

        if c == "\n":
            self.line_number += 1
            self.char_number = 1

        return c

    def skip(self) -> str:
        """Gets the next non-whitespace character from the input stream

        Returns:
            str: The next non-whitespace character from the input stream
        """
        c: str = self.next_character()
        while c.isspace():
            c = self.next_character()
        return c

    def put_back(self, c: str) -> None:
        """Put a character back into the input stream

        Args:
            c (str): Character to put back into the input stream
        """
        if len(c) != 1:
            raise TypeError(
                f"put_back() expected a character, but string of length {len(c)} found"
            )

        self.put_back_buffer = c

    def scan_integer_literal(self, c: str) -> int:
        """Scan integer literals into a buffer and parse them into int objects

        Args:
            c (str): Current character from input stream

        Returns:
            int: Scanned integer literal
        """
        in_string: str = ""

        while c.isdigit():
            in_string += c
            c = self.next_character()

        self.put_back(c)

        return int(in_string)

    def scan_identifier(self, c: str) -> str:
        """Scan identifier strings into a buffer

        Args:
            c (str): Current character from input stream

        Raises:
            EccoIdentifierError: If identifier is too long

        Returns:
            str: Scanned identifier buffer
        """
        identifier: str = ""

        while c.isalpha() or c == "_":
            identifier += c
            c = self.next_character()

            # I've picked an arbitrary limit for identifier length,
            # although other implementations of C have larger limits
            if len(identifier) >= 512:
                raise EccoIdentifierError("Identifier is too long!")

        self.put_back(c)

        return identifier

    def scan(self) -> Token:
        """Scan the next token

        Raises:
            EccoSyntaxError: If an unrecognized Token is reached

        Returns:
            Token: A Token object with the latest scanned data, or None if EOF is reached
        """
        c: str = self.skip()
        self.current_token = Token()

        # Check for EOF
        if c == "":
            self.current_token.type = TokenType.EOF
            return self.current_token

        possible_token_type = TokenType.from_string(c)

        if possible_token_type == TokenType.UNKNOWN_TOKEN:
            if c.isdigit():
                self.current_token.type = TokenType.INTEGER_LITERAL
                self.current_token.value = self.scan_integer_literal(c)
            elif c.isalpha() or c == "_":
                print("Found identifier")
                scanned_identifier: str = self.scan_identifier(c)
                print("Scanned identifier", scanned_identifier)

                if scanned_identifier in TokenType.string_values():
                    self.current_token.type = TokenType.from_string(scanned_identifier)
                else:
                    raise EccoSyntaxError(
                        f'Unrecognized identifier "{scanned_identifier}"'
                    )
            else:
                raise EccoSyntaxError(f'Uncrecognized token "{c}"')
        else:
            self.current_token.type = possible_token_type

        return self.current_token

    def scan_file(self) -> None:
        """Scans a file and prints out its Tokens"""
        while self.scan():
            print(self.current_token)
