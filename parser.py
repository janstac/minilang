from dataclasses import dataclass
import lexer


@dataclass
class BinaryOp:
    operator: str
    left: "Expression"
    right: "Expression"


@dataclass
class UnaryOp:
    operator: str
    expr: "Expression"


@dataclass
class Identifier:
    name: str


@dataclass
class StatementBlock:
    l: list["Statement"]


@dataclass
class IntegerLiteral:
    n: int

@dataclass
class LetStatement:
    identifier: Identifier
    value: "Expression"

@dataclass
class SetStatement:
    identifier: Identifier
    value: "Expression"


@dataclass
class IfStatement:
    condition: "Expression"
    true_branch: "Statement"
    else_branch: "Statement | None"


@dataclass
class WhileStatement:
    condition: "Expression"
    statement: "Statement"


@dataclass
class InputValue:
    pass

@dataclass
class OutputStatement:
    value: "Expression"


Expression = UnaryOp | BinaryOp | Identifier | IntegerLiteral | InputValue

Statement = (
    SetStatement
    | LetStatement
    | IfStatement
    | StatementBlock
    | WhileStatement
    | OutputStatement
)
TreeNode = Expression | Statement

binary_ops_precedence = {"==": 0, "*": 5, "/": 5, "+": 4, "-": 4, "AND": 3, "OR": 2}


class Parser:
    def __init__(self, tokens: list[lexer.Token]):
        self.tokens = tokens
        self.token_index = -1
        self.current_token: lexer.Token | None = None
        self.next_token()

    def next_token(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = None

    def accept_token(self, token: lexer.Token | None) -> bool:
        if self.current_token == token:
            self.next_token()
            return True
        return False

    def assert_token(self, token: lexer.Token | None):
        assert self.accept_token(token)

    # def accept_identifier(self) -> str:
    #     if isinstance(self.current)

    def accept_type[T: lexer.Token](self, token_type: type[T]) -> T | None:
        """
        Returns current token and moves to next token if current token has type token_type
        Otherwise, returns none
        """
        if isinstance(self.current_token, token_type):
            t = self.current_token
            self.next_token()
            return t
        else:
            return None

    def expect[T: lexer.Token](self, token: T | None) -> T:
        assert token is not None
        return token

    def parse_statements(self) -> StatementBlock:
        statements_list = []
        while self.current_token not in [None, lexer.SpecialChar("}")]:
            if self.current_token != lexer.SpecialChar(";"):
                statements_list.append(self.parse_statement())
            self.assert_token(lexer.SpecialChar(";"))
        return StatementBlock(statements_list)

    def parse_program(self) -> StatementBlock:
        statements = self.parse_statements()
        self.assert_token(None)
        return statements

    def parse_statement(self) -> Statement:
        if self.accept_token(lexer.Keyword("if")):
            condition = self.parse_expr()
            true_branch = self.parse_statement()
            else_branch = None
            if self.accept_token(lexer.Keyword("else")):
                else_branch = self.parse_statement()
            return IfStatement(condition, true_branch, else_branch)
        elif self.accept_token(lexer.Keyword("while")):
            condition = self.parse_expr()
            block = self.parse_statement()
            return WhileStatement(condition, block)
        elif self.accept_token(lexer.Keyword("set")):
            identifier = Identifier(
                self.expect(self.accept_type(lexer.Identifier)).name
            )
            self.assert_token(lexer.SpecialChar("="))
            value = self.parse_expr()
            return SetStatement(identifier, value)
        elif self.accept_token(lexer.Keyword("let")):
            identifier = Identifier(
                self.expect(self.accept_type(lexer.Identifier)).name
            )
            self.assert_token(lexer.SpecialChar("="))
            value = self.parse_expr()
            return LetStatement(identifier, value)
        elif self.accept_token(lexer.SpecialChar("{")):
            statement_block = self.parse_statements()
            self.assert_token(lexer.SpecialChar("}"))
            return statement_block
        elif self.accept_token(lexer.Keyword("output")):
            expression = self.parse_expr()
            return OutputStatement(expression)
        else:
            assert False

    def parse_expr(self) -> Expression:
        return self.parse_expr_precedence(-1)

    def parse_expr_precedence(self, current_precedence: int) -> Expression:
        return self.parse_expr_binary_op(self.parse_expr_term(), current_precedence)

    # A term is a part of an expression between binary operators
    def parse_expr_term(self) -> Expression:
        # unary operator
        if self.accept_token(lexer.Keyword("NOT")):
            return UnaryOp("NOT", self.parse_expr_term())
        elif self.accept_token(lexer.SpecialChar("-")):
            return UnaryOp("-", self.parse_expr_term())
        # `( expr )`
        elif self.accept_token(lexer.SpecialChar("(")):
            expr = self.parse_expr()
            self.assert_token(lexer.SpecialChar(")"))
        elif self.current_token == lexer.SpecialChar(")"):
            assert False
        elif isinstance(self.current_token, lexer.Integer):
            expr = IntegerLiteral(self.current_token.n)
            self.next_token()
        elif self.accept_token(lexer.Keyword("input")):
            expr = InputValue()
        # `identifier`
        else:
            expr = Identifier(self.expect(self.accept_type(lexer.Identifier)).name)
        return expr

    def parse_expr_binary_op(
        self, left: Expression, current_precedence: int
    ) -> Expression:
        # print("__1", left, current_precedence, self.current_token)
        t = self.current_token
        if isinstance(t, lexer.Keyword) and t.word in binary_ops_precedence:
            op = t.word
        elif isinstance(t, lexer.SpecialChar) and t.char in binary_ops_precedence:
            op = t.char
        else:
            return left

        op_precedence = binary_ops_precedence[op]
        if current_precedence < op_precedence:
            # print("__3")
            self.next_token()
            right = self.parse_expr_precedence(op_precedence)
            new_left = BinaryOp(op, left, right)
            return self.parse_expr_binary_op(new_left, current_precedence)
        else:
            return left
        # print("__2")
        # binary_op = binary_ops[type(self.current_token)]


def syntax_string(node: TreeNode) -> str:
    match node:
        case UnaryOp(operator, expr):
            s = f"{operator} {syntax_string(expr)}"
        case Identifier(name):
            s = name
        case BinaryOp(operator, left, right):
            s = f"({syntax_string(left)} {operator} {syntax_string(right)})"
        case IntegerLiteral(n):
            s = str(n)
        case StatementBlock(statement_list):
            s = "{\n"
            for statement in statement_list:
                s += syntax_string(statement) + ";\n"
            s += "}"
        case IfStatement(condition, true_branch, else_branch):
            s = f"if {syntax_string(condition)} {syntax_string(true_branch)}"
            if else_branch is not None:
                s += f" else {syntax_string(else_branch)}"
        case WhileStatement(condition, block):
            s = f"while {syntax_string(condition)} {syntax_string(block)}"
        case SetStatement(identifier, value):
            s = f"set {syntax_string(identifier)} = {syntax_string(value)}"
        case LetStatement(identifier, value):
            s = f"let {syntax_string(identifier)} = {syntax_string(value)}"
        case InputValue():
            s = f"input"
        case OutputStatement(expression):
            s = f"output {syntax_string(expression)}"
    print()
    return s


def test(text):
    a = Parser(lexer.tokenise(text))
    e = a.parse_program()
    print(e)
    # print(syntax_string(e))


if __name__ == "__main__":
    test(input())

# print(parse(tokeniser.tokenise(input())))

# Recursive descent
