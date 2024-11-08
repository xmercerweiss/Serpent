
def raise_error(*args, e, msg):
    formatted = msg.format(*args)
    raise e(formatted)
