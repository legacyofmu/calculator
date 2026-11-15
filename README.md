# Calculator

Python 3.12 + tkinter로 만든 데스크톱 계산기입니다. git / GitHub 학습용 예제 프로젝트입니다.

## 기능

- **일반 모드**: 사칙연산, 퍼센트, 부호 전환, 괄호
- **공학용 모드**: 삼각함수(sin, cos, tan 및 역함수), 로그(log, ln), 제곱/제곱근, 거듭제곱, 팩토리얼, π, e, DEG/RAD 전환
- **계산 기록**: 최근 계산 50개 보관, 항목 클릭 시 결과 불러오기

## 실행 방법

```bash
python main.py
```

## 테스트

```bash
python -m unittest discover -s tests -v
```

## 단축키

| 키 | 동작 |
|---|---|
| `Enter` 또는 `=` | 계산 |
| `Backspace` | 한 글자 지우기 |
| `Esc` | 전체 지우기 |
| `^` | 거듭제곱 |
