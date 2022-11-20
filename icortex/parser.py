import re


def extract_quoted_string(s):
    s = s.lstrip()
    if s[0] == '"' or s[0] == "'":
        ret = s[1 : s.find(s[0], 1)]
        rest = s[s.find(s[0], 1) + 1 :].strip()
        surrounded = True
    else:
        ret = s
        rest = ""
        surrounded = False
    return ret, rest, surrounded


def extract_prompt(raw_prompt):
    raw_prompt, rest, surrounded = extract_quoted_string(raw_prompt)
    if surrounded:
        return raw_prompt, rest

    flag_regex = re.compile(r"(?:-[a-zA-Z]|--[a-zA-Z]+)")
    flag_match = flag_regex.search(raw_prompt)

    if flag_match:
        ret = raw_prompt[: flag_match.start()].strip()
        rest = raw_prompt[flag_match.start() :]
    else:
        ret = raw_prompt.strip()
        rest = ""

    return ret, rest


def lex_prompt(raw_prompt):
    prompt, rest = extract_prompt(raw_prompt)
    ret = [prompt]
    # Split rest and remove empty strings
    ret.extend([s for s in rest.split() if s])
    return ret
