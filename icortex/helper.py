from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer


def unescape(s) -> str:
    return s.encode("utf-8").decode("unicode_escape")


def is_prompt(input: str) -> bool:
    return input.strip().split()[0] in [
        r"%p",
        r"%prompt",
        r"%%prompt",
        r"%%prompt",
    ]


def is_cli(input: str) -> bool:
    return input.strip().split()[0] == r"%icortex"


def escape_quotes(s: str) -> str:
    return s.replace('"', r"\"").replace("'", r"\'")


def extract_prompt(input: str) -> str:
    tokens = input.strip().split(" ", 1)
    if len(tokens) == 1:
        return ""
    else:
        return tokens[1]


extract_cli = extract_prompt


def yes_no_input(message: str, default=True) -> bool:
    if default:
        message += " [Y/n]"
    else:
        message += " [y/N]"

    print(message)
    user_input = input()

    return (user_input == "" and default) or user_input.strip().lower() == "y"


def prompt_input(message: str, type=str, default=None):
    if default:
        message += f" [{default}]"

    print(message)
    user_input = input()

    if user_input == "" and default is not None:
        return default
    else:
        return type(user_input)


def highlight_python(code: str):
    return highlight(code, PythonLexer(), Terminal256Formatter())
