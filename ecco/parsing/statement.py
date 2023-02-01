from .ecco_ast import ASTNode
from ..scanning import TokenType
from .expression import parse_binary_expression
from ..utils import EccoSyntaxError
from typing import Generator


def match_token(tt: TokenType) -> None:
    from ..ecco import GLOBAL_SCANNER

    if GLOBAL_SCANNER.current_token.type == tt:
        GLOBAL_SCANNER.scan()
        return

    raise EccoSyntaxError(
        f'Expected "{str(tt)}" but got "{str(GLOBAL_SCANNER.current_token.type)}"'
    )


def parse_statements() -> Generator[ASTNode, None, None]:
    from ..ecco import GLOBAL_SCANNER

    tree: ASTNode

    while GLOBAL_SCANNER.current_token.type != TokenType.EOF:
        match_token(TokenType.PRINT)

        tree = parse_binary_expression(0)

        match_token(TokenType.SEMICOLON)

        # generate_llvm(tree)
        yield tree