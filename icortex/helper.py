import traceback
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer

from IPython.core.interactiveshell import ExecutionResult, ExecutionInfo


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


def unescape_quotes(s: str) -> str:
    return s.replace(r"\"", '"').replace(r"\'", "'")


# def extract_prompt(input: str) -> str:
#     tokens = input.strip().split(" ", 1)
#     if len(tokens) == 1:
#         return ""
#     else:
#         return tokens[1]


# extract_cli = extract_prompt


def yes_no_input(message: str, default=True) -> bool:
    if default:
        message += " [Y/n]"
    else:
        message += " [y/N]"

    print(message)
    user_input = input()

    return (user_input == "" and default) or user_input.strip().lower() == "y"


def prompt_input(message: str, type=str, default=None, press_enter=False):
    if default:
        message += f" {default}"
        if press_enter:
            message += "  (Press enter to select the default option)"

    print(message)
    user_input = input()

    if user_input == "" and default is not None:
        return default
    else:
        return type(user_input)


def highlight_python(code: str):
    return highlight(code, PythonLexer(), Terminal256Formatter())


def serialize_exception(exception):
    ret = {
        "name": exception.__class__.__name__,
        "message": str(exception),
    }
    try:
        # This raises errors for certain exceptions.
        # Can't consider every edge case now, let's hope
        # "message" will contain enough information
        ret["traceback"] = traceback.format_exc(exception)
    except:
        pass

    return ret


def serialize_execution_result(execution_result: ExecutionResult):
    ret = {}
    if execution_result.error_before_exec is not None:
        ret["error_before_exec"] = serialize_exception(
            execution_result.error_before_exec
        )
    if execution_result.error_in_exec is not None:
        ret["error_in_exec"] = serialize_exception(execution_result.error_in_exec)
    if execution_result.result is not None:
        # TODO: Are we ever going to need deeper serialization?
        ret["result"] = str(execution_result.result)
    ret["success"] = execution_result.success
    return ret


def deserialize_execution_result(execution_result: dict):
    # TODO: Deserialize the execution result and info better
    ret = ExecutionResult(ExecutionInfo("", False, None, None, None))

    # No need to set success, it's a property. See ExecutionResult.success
    # ret.success = execution_result["success"]
    if "error_before_exec" in execution_result:
        ret.error_before_exec = deserialize_exception(
            execution_result["error_before_exec"]
        )
    if "error_in_exec" in execution_result:
        ret.error_in_exec = deserialize_exception(execution_result["error_in_exec"])
    if "result" in execution_result:
        ret.result = execution_result["result"]
    return ret


def deserialize_exception(exception: dict):
    # TODO: This is a hack, we need to deserialize the exception properly
    return Exception(exception["message"])


def is_icortex_magic(raw_cell: str) -> bool:
    raw_cell = raw_cell.strip()
    return (
        raw_cell.startswith(r"%icortex ")
        or raw_cell.startswith(r"%prompt ")
        or raw_cell.startswith(r"%%prompt ")
        or raw_cell.startswith(r"%p ")
        or raw_cell.startswith(r"%%p ")
        or raw_cell.startswith(r"%var ")
    )


def is_magic(raw_cell: str) -> bool:
    raw_cell = raw_cell.strip()
    return raw_cell.startswith("%")


def comment_out(input: str) -> str:
    ret = "# " + input
    ret = ret.replace("\n", "\n# ")
    return ret
