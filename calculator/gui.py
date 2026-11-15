"""tkinter 기반 계산기 화면."""

import tkinter as tk

from .engine import CalcError, Engine, format_number

# 일반 모드 버튼 배치: (표시 글자, 입력값 또는 동작)
BASIC_BUTTONS = [
    [("C", "clear"), ("⌫", "back"), ("%", "percent"), ("÷", "÷")],
    [("7", "7"), ("8", "8"), ("9", "9"), ("×", "×")],
    [("4", "4"), ("5", "5"), ("6", "6"), ("−", "−")],
    [("1", "1"), ("2", "2"), ("3", "3"), ("+", "+")],
    [("±", "negate"), ("0", "0"), (".", "."), ("=", "equals")],
]

COLORS = {
    "bg": "#1e1e1e",
    "display": "#252526",
    "text": "#ffffff",
    "num": "#3c3c3c",
    "op": "#505050",
    "equals": "#0a84ff",
}


class CalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.configure(bg=COLORS["bg"])
        self.resizable(False, False)

        self.engine = Engine()
        self.expression = ""
        self.just_evaluated = False

        self._build_display()
        self.keypad = tk.Frame(self, bg=COLORS["bg"])
        self.keypad.pack(padx=8, pady=(0, 8))
        self._build_keypad()
        self._bind_keys()

    # ---------- 화면 구성 ----------
    def _build_display(self):
        frame = tk.Frame(self, bg=COLORS["display"])
        frame.pack(fill="x", padx=8, pady=8)
        self.history_var = tk.StringVar()
        self.display_var = tk.StringVar(value="0")
        tk.Label(frame, textvariable=self.history_var, anchor="e", bg=COLORS["display"],
                 fg="#9e9e9e", font=("Segoe UI", 11)).pack(fill="x", padx=10, pady=(8, 0))
        tk.Label(frame, textvariable=self.display_var, anchor="e", bg=COLORS["display"],
                 fg=COLORS["text"], font=("Segoe UI", 26, "bold"), width=16).pack(
            fill="x", padx=10, pady=(0, 8))

    def _build_keypad(self):
        for r, row in enumerate(BASIC_BUTTONS):
            for c, (label, action) in enumerate(row):
                self._make_button(self.keypad, label, action, r, c)

    def _make_button(self, parent, label, action, row, col):
        if action == "equals":
            color = COLORS["equals"]
        elif label.isdigit() or label == ".":
            color = COLORS["num"]
        else:
            color = COLORS["op"]
        btn = tk.Button(parent, text=label, width=5, height=2, bg=color, fg=COLORS["text"],
                        activebackground="#6e6e6e", activeforeground=COLORS["text"],
                        relief="flat", font=("Segoe UI", 14),
                        command=lambda a=action: self.on_press(a))
        btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
        return btn

    def _bind_keys(self):
        for ch in "0123456789.+-*/()%":
            self.bind(ch, lambda e, ch=ch: self.on_press({"*": "×", "/": "÷", "-": "−"}.get(ch, ch)))
        self.bind("<Return>", lambda e: self.on_press("equals"))
        self.bind("=", lambda e: self.on_press("equals"))
        self.bind("<BackSpace>", lambda e: self.on_press("back"))
        self.bind("<Escape>", lambda e: self.on_press("clear"))

    # ---------- 동작 ----------
    def on_press(self, action):
        if action == "clear":
            self.expression = ""
            self.history_var.set("")
        elif action == "back":
            self.expression = self.expression[:-1]
        elif action == "equals":
            self._evaluate()
            return
        elif action == "negate":
            self.expression = f"−({self.expression})" if self.expression else "−"
        elif action == "percent":
            if self.expression:
                self.expression = f"({self.expression})÷100"
                self._evaluate()
                return
        else:
            # 결과 직후 숫자를 누르면 새 계산 시작, 연산자면 결과에 이어서 계산
            if self.just_evaluated and (action[0].isdigit() or action == "."):
                self.expression = ""
            self.expression += action
        self.just_evaluated = False
        self._refresh()

    def _evaluate(self):
        if not self.expression:
            return
        try:
            result = format_number(self.engine.evaluate(self.expression))
        except CalcError as e:
            self.history_var.set(self.expression)
            self.display_var.set(str(e))
            self.expression = ""
            return
        self.history_var.set(self.expression + " =")
        self.expression = result
        self.just_evaluated = True
        self._refresh()

    def _refresh(self):
        self.display_var.set(self.expression or "0")
