"""계산 엔진: 문자열 수식을 안전하게 계산한다.

파이썬의 eval()은 임의 코드를 실행할 수 있어 위험하므로,
ast 모듈로 수식을 파싱한 뒤 허용된 연산만 직접 계산한다.
"""

import ast
import math
import operator


class CalcError(Exception):
    """잘못된 수식이나 계산 불가능한 경우 발생."""


def _power(base, exp):
    # 너무 큰 거듭제곱은 메모리/시간을 소모하므로 제한
    if abs(exp) > 10000:
        raise OverflowError
    return operator.pow(base, exp)


def _factorial(x):
    if x != int(x) or x < 0 or x > 170:
        raise ValueError
    return math.factorial(int(x))


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: _power,
}

_CONSTANTS = {"pi": math.pi, "e": math.e}

# 각도 단위의 영향을 받지 않는 함수
_FUNCTIONS = {
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "exp": math.exp,
    "abs": abs,
    "fact": _factorial,
}

_TRIG = {"sin": math.sin, "cos": math.cos, "tan": math.tan}
_INV_TRIG = {"asin": math.asin, "acos": math.acos, "atan": math.atan}

_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class Engine:
    def __init__(self, degrees: bool = True):
        # True면 삼각함수 각도를 도(DEG), False면 라디안(RAD)으로 해석
        self.degrees = degrees

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
        return (expression.replace("×", "*").replace("÷", "/").replace("−", "-")
                .replace("^", "**").replace("π", "pi").replace("√", "sqrt"))

    def _eval(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
            return _BIN_OPS[type(node.op)](self._eval(node.left), self._eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
            return _UNARY_OPS[type(node.op)](self._eval(node.operand))
        if isinstance(node, ast.Name) and node.id in _CONSTANTS:
            return _CONSTANTS[node.id]
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and len(node.args) == 1 and not node.keywords):
            return self._call(node.func.id, self._eval(node.args[0]))
        raise CalcError("지원하지 않는 수식")

    def _call(self, name, arg):
        if name in _FUNCTIONS:
            return _FUNCTIONS[name](arg)
        if name in _TRIG:
            rad = math.radians(arg) if self.degrees else arg
            if name == "tan" and math.isclose(math.cos(rad), 0, abs_tol=1e-15):
                raise ValueError  # tan(90°) 등 정의되지 않음
            return _clean(_TRIG[name](rad))
        if name in _INV_TRIG:
            result = _INV_TRIG[name](arg)
            return math.degrees(result) if self.degrees else result
        raise CalcError(f"알 수 없는 함수: {name}")


def _clean(x):
    """sin(180°)=1.2e-16 같은 부동소수점 오차를 0으로 정리."""
    return 0.0 if abs(x) < 1e-12 else x


def format_number(value: float) -> str:
    """결과를 보기 좋게 표시한다 (정수면 소수점 제거, 긴 소수는 반올림)."""
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise CalcError("계산 범위 오류")
        if value.is_integer() and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.12g}"
    return str(value)
