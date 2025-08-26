from collections.abc import Iterable
from itertools import chain
import random
import re

PATTERNS = (
    ("NUMBER", r"\d+"),
    ("ADD",    r"\+"),
    ("DICE",    r"\.")
)
JOINED_PATTERN = "|".join(f"(?P<{name}>{pattern})" for name, pattern in PATTERNS)
PATTERN = re.compile(JOINED_PATTERN)


class Token:
    pass


class Operator(Token):
    pass


class Add(Operator):
    pass


class Dice(Operator):
    pass


class Number(Token):
    def __init__(self, value: int):
        self.value = value


def tokenize(input: str):
    for match_obj in PATTERN.finditer(input):
        match match_obj.lastgroup:
            case "ADD":
                yield Add()
            case "DICE":
                yield Dice()
            case "NUMBER":
                yield Number(int(match_obj.group()))
            case _:
                raise ValueError("tokenizer fail")


def infix_to_postfix(token_sequence: Iterable[Token]):
    """Converts infix sequence to postfix using the shunting yard algorithm."""
    stack = []
    for token in token_sequence:
        if isinstance(token, Dice):  # highest precedence
            stack.append(token)
        elif isinstance(token, Add):
            if len(stack) > 0 and isinstance(stack[-1], Dice):
                yield stack.pop()
            stack.append(token)
        elif isinstance(token, Number):
            yield token
        else:
            raise RuntimeError("infix_to_postfix error: unknown token")

    while len(stack) > 0:
        yield stack.pop()


def evaluate_postfix(token_sequence: Iterable[Token]):
    stack: list[int] = []
    for token in token_sequence:
        if isinstance(token, Number):
            stack.append(token.value)
        elif isinstance(token, Add):
            right = stack.pop()
            left = stack.pop()
            result = right + left
            stack.append(result)
        elif isinstance(token, Dice):
            right = stack.pop()
            left = stack.pop()
            result = evaluate_dice(left, right)
            stack.append(result)

    if len(stack) != 1:
        raise RuntimeError("evaluation error: unexpected number of results")

    return stack.pop()


def evaluate_dice(multiplier, dice):
    result = 0
    for i in range(multiplier):
        result += random.randint(1, dice)
    return result


if __name__ == "__main__":
    while True:
        input_str = input(">>> ")
        result = evaluate_postfix(infix_to_postfix(tokenize(input_str)))
        print(result)