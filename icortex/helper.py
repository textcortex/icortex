def unescape(s):
    return s.encode("utf-8").decode("unicode_escape")


def is_prompt(input: str):
    return input.strip()[0] == "/"


def extract_prompt(input: str):
    return input.strip()[1:].strip()
