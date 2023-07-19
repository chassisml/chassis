def deprecated(message: str = None):
    msg = "DEPRECATION WARNING: This method will be removed in the next major release."
    if message is not None:
        msg += " " + message
    print(msg)
