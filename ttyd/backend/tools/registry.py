TOOLS = {}


def register_tool(name):
    def wrapper(fn):
        TOOLS[name] = fn
        return fn

    return wrapper
