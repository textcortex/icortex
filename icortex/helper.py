def unescape(s):
    return s.encode("utf-8").decode("unicode_escape")


def is_prompt(input: str):
    return input.strip()[0] == "/"

def escape_quotes(s: str):
    return s.replace('"', r"\"").replace("'", r"\'")


def extract_prompt(input: str):
    return input.strip()[1:].strip()

def yes_no_input(message: str, default=True):
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


