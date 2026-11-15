"""tkinter 기반 계산기 화면."""

import tkinter as tk

from .engine import CalcError, Engine, format_number
from .history import History

# 일반 모드 버튼 배치: (표시 글자, 입력값 또는 동작)
BASIC_BUTTONS = [
    [("C", "clear"), ("⌫", "back"), ("%", "percent"), ("÷", "÷")],
    [("7", "7"), ("8", "8"), ("9", "9"), ("×", "×")],
    [("4", "4"), ("5", "5"), ("6", "6"), ("−", "−")],
    [("1", "1"), ("2", "2"), ("3", "3"), ("+", "+")],
    [("±", "negate"), ("0", "0"), (".", "."), ("=", "equals")],
]

# 공학용 모드에서 왼쪽에 추가되는 버튼
SCIENTIFIC_BUTTONS = [
    [("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("(", "(")],
    [("sin⁻¹", "asin("), ("cos⁻¹", "acos("), ("tan⁻¹", "atan("), (")", ")")],
    [("x²", "^2"), ("xʸ", "^"), ("√", "√("), ("n!", "fact(")],
    [("log", "log("), ("ln", "ln("), ("eˣ", "exp("), ("|x|", "abs(")],
    [("π", "π"), ("e", "e"), ("1/x", "inverse"), ("DEG", "angle")],
]

# 계산 결과 바로 뒤에 눌렀을 때 결과에 이어서 계산하는 입력
_CONTINUE_PREFIXES = ("+", "−", "×", "÷", "^", ")", "%")

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

        self.engine = Engine(degrees=True)
        self.expression = ""
        self.just_evaluated = False
        self.scientific = False
        self.history = History()

        self._build_mode_bar()
        self._build_display()
        self.keypad = tk.Frame(self, bg=COLORS["bg"])
        self.keypad.pack(padx=8, pady=(0, 8))
        self._build_keypad()
        self._build_history_panel()
        self._bind_keys()

    # ---------- 화면 구성 ----------
    def _build_mode_bar(self):
        bar = tk.Frame(self, bg=COLORS["bg"])
        bar.pack(fill="x", padx=8, pady=(8, 0))
        self.mode_buttons = {}
        for name, label in (("basic", "일반"), ("scientific", "공학용")):
            btn = tk.Button(bar, text=label, relief="flat", font=("Segoe UI", 10),
                            fg=COLORS["text"], activeforeground=COLORS["text"],
                            command=lambda n=name: self.set_mode(n == "scientific"))
            btn.pack(side="left", padx=(0, 4))
            self.mode_buttons[name] = btn
        self.history_button = tk.Button(bar, text="기록", relief="flat", font=("Segoe UI", 10),
                                        bg=COLORS["op"], fg=COLORS["text"],
                                        activeforeground=COLORS["text"],
                                        command=self.toggle_history)
        self.history_button.pack(side="right")
        self._update_mode_bar()

    def _build_history_panel(self):
        """계산 기록 패널 (기본은 숨김, '기록' 버튼으로 표시)."""
        self.history_frame = tk.Frame(self, bg=COLORS["bg"])
        self.history_list = tk.Listbox(self.history_frame, height=6, bg=COLORS["display"],
                                       fg=COLORS["text"], selectbackground=COLORS["equals"],
                                       font=("Segoe UI", 11), relief="flat",
                                       highlightthickness=0, activestyle="none")
        self.history_list.pack(fill="x")
        self.history_list.bind("<<ListboxSelect>>", self._on_history_select)
        tk.Button(self.history_frame, text="기록 지우기", relief="flat", font=("Segoe UI", 9),
                  bg=COLORS["op"], fg=COLORS["text"], activeforeground=COLORS["text"],
                  command=self.clear_history).pack(anchor="e", pady=(4, 0))
        self.history_visible = False

    def toggle_history(self):
        if self.history_visible:
            self.history_frame.pack_forget()
        else:
            self.history_frame.pack(fill="x", padx=8, pady=(0, 8), before=self.keypad)
        self.history_visible = not self.history_visible
        self.history_button.configure(
            bg=COLORS["equals"] if self.history_visible else COLORS["op"])

    def clear_history(self):
        self.history.clear()
        self._refresh_history()

    def _refresh_history(self):
        self.history_list.delete(0, "end")
        for entry in self.history.entries:
            self.history_list.insert("end", str(entry))

    def _on_history_select(self, _event):
        selection = self.history_list.curselection()
        if not selection:
            return
        entry = self.history.entries[selection[0]]
        self.expression = entry.result
        self.just_evaluated = True
        self._refresh()

    def _update_mode_bar(self):
        active = "scientific" if self.scientific else "basic"
        for name, btn in self.mode_buttons.items():
            btn.configure(bg=COLORS["equals"] if name == active else COLORS["op"])

    def set_mode(self, scientific: bool):
        if scientific == self.scientific:
            return
        self.scientific = scientific
        for child in self.keypad.winfo_children():
            child.destroy()
        self._build_keypad()
        self._update_mode_bar()

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
        offset = 0
        if self.scientific:
            for r, row in enumerate(SCIENTIFIC_BUTTONS):
                for c, (label, action) in enumerate(row):
                    btn = self._make_button(self.keypad, label, action, r, c)
                    btn.configure(font=("Segoe UI", 12))
                    if action == "angle":
                        self.angle_button = btn
                        self._update_angle_label()
            offset = len(SCIENTIFIC_BUTTONS[0])
        for r, row in enumerate(BASIC_BUTTONS):
            for c, (label, action) in enumerate(row):
                self._make_button(self.keypad, label, action, r, c + offset)

    def _update_angle_label(self):
        self.angle_button.configure(text="DEG" if self.engine.degrees else "RAD")

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
        for ch in "0123456789.+-*/()%^":
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
        elif action == "inverse":
            if self.expression:
                self.expression = f"1÷({self.expression})"
                self._evaluate()
                return
        elif action == "angle":
            self.engine.degrees = not self.engine.degrees
            self._update_angle_label()
            return
        else:
            # 결과 직후 연산자를 누르면 결과에 이어서 계산, 그 외(숫자·함수)는 새 계산 시작
            if self.just_evaluated and not action.startswith(_CONTINUE_PREFIXES):
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
        self.history.add(self.expression, result)
        self._refresh_history()
        self.expression = result
        self.just_evaluated = True
        self._refresh()

    def _refresh(self):
        self.display_var.set(self.expression or "0")
