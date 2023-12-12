from collections import deque
import parser


class Interpreter:
    def __init__(self, program: parser.Statement) -> None:
        self.program = program
        self.variableStack = deque[dict[str, int]]()

    def run(self):
        self.run_statement_with_scope(self.program)

    def get_scope_index(self, identifier: str) -> int | None:
        for i in range(len(self.variableStack) - 1, -1, -1):
            scope = self.variableStack[i]
            if identifier in scope:
                return i
        return None

    def eval_expr(self, expr: parser.Expression) -> int:
        match expr:
            case parser.UnaryOp("-", expr2):
                return - self.eval_expr(expr2)
            case parser.UnaryOp("NOT", expr2):
                if self.eval_expr(expr2) == 0:
                    return 1
                else:
                    return 0
            case parser.UnaryOp(_, _):
                assert False, "Unknown unary operator"
            case parser.BinaryOp(operator, left, right):
                left_value = self.eval_expr(left)
                right_value = self.eval_expr(right)
                match operator:
                    case "+":
                        value = left_value + right_value
                    case "-":
                        value = left_value - right_value
                    case "*":
                        value = left_value * right_value
                    case "/":
                        value = left_value // right_value
                    case "AND":
                        value = 1 if left_value !=0 and right_value !=0 else 0
                    case "OR":
                        value = 1 if left_value !=0 or right_value !=0 else 0
                    case "==":
                        value = 1 if left_value == right_value else 0
                    case _:
                        assert False, "Unknown binary operator"
                return value
            case parser.Identifier(name):
                scope_index = self.get_scope_index(name)
                if scope_index is None:
                    raise Exception(f"Variable {name} not defined")
                value = self.variableStack[scope_index][name]
                # if value is None:
                #     raise Exception(f"Variable {name} not initialized")
                return value
            case parser.InputValue():
                while True:
                    try:
                        value = int(input())
                    except ValueError:
                        print("Input must be an integer")
                        continue
                    break
                return value
            case parser.IntegerLiteral(n):
                return n
            case _:
                assert False, "Unknown expression type"
                        

    def run_statement_with_scope(self, statement: parser.Statement):
        self.variableStack.append({})
        self.run_statement(statement)
        self.variableStack.pop()

    def run_statement(self, statement: parser.Statement):
        match statement:
            case parser.IfStatement():
                if self.eval_expr(statement.condition) == 1:
                    self.run_statement_with_scope(statement.true_branch)
                elif statement.else_branch is not None:
                    self.run_statement_with_scope(statement.else_branch)
            case parser.WhileStatement():
                while self.eval_expr(statement.condition) == 1:
                    self.run_statement_with_scope(statement.statement)
            case parser.LetStatement():
                value = self.eval_expr(statement.value)
                if statement.identifier.name in self.variableStack[-1]:
                    raise Exception(f"Variable {statement.identifier.name} already defined in this scope")
                self.variableStack[-1][statement.identifier.name] = value
            case parser.SetStatement():
                scope_index = self.get_scope_index(statement.identifier.name)
                if scope_index is None:
                    raise Exception(f"Variable {statement.identifier.name} not defined")
                value = self.eval_expr(statement.value)
                self.variableStack[scope_index][statement.identifier.name] = value
            case parser.StatementBlock():
                for s in statement.l:
                    self.run_statement(s)
            case parser.OutputStatement():
                value = self.eval_expr(statement.value)
                print(value)
            case _:
                assert False, "Unknown statement type"
                    

