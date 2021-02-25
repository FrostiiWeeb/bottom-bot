from .bottom import from_bottom, to_bottom


def get_code(codeblock: str):
    code = codeblock.splitlines()
    if code[0].startswith("```"):
        code.pop(0)

    if code[len(code) - 1].endswith("```"):
        if len(code[len(code) - 1]) > 3:
            code = code[len(code) - 1][:-3]
        else:
            code.pop(len(code) - 1)

    return "".join(code)