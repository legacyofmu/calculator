"""계산 엔진: 문자열 수식을 안전하게 계산한다.

파이썬의 eval()은 임의 코드를 실행할 수 있어 위험하므로,
ast 모듈로 수식을 파싱한 뒤 허용된 연산만 직접 계산한다.
"""

import ast
import operator


class CalcError(Exception):
    """잘못된 수식이나 계산 불가능한 경우 발생."""


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
}

_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class Engine:
    def evaluate(self, expression: str) -> float:
        expr = self._normalize(expression)
        if not expr.strip():
            raise CalcError("빈 수식")
        try:
            tree = ast.parse(expr, mode="eval")
        except SyntaxError as e:
            raise CalcError("수식 오류") from e
        try:
            return self._eval(tree.body)
        except ZeroDivisionError as e:
            raise CalcError("0으로 나눌 수 없음") from e
        except (OverflowError, ValueError) as e:
            raise CalcError("계산 범위 오류") from e

    @staticmethod
    def _normalize(expression: str) -> str:
        """화면 표시용 기호를 파이썬 연산자로 바꾼다."""
        return expression.replace("×", "*").replace("÷", "/").replace("−", "-")

    def _eval(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
            return _BIN_OPS[type(node.op)](self._eval(node.left), self._eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
            return _UNARY_OPS[type(node.op)](self._eval(node.operand))
        raise CalcError("지원하지 않는 수식")


def format_number(value: float) -> str:
    """결과를 보기 좋게 표시한다 (정수면 소수점 제거, 긴 소수는 반올림)."""
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise CalcError("계산 범위 오류")
        if value.is_integer() and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.12g}"
    return str(value)
