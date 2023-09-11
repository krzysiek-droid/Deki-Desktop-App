
def log_exception(e):
    import inspect
    """
    Construct a log string with the class name, function name, and exception.

    :param e: The exception object that was raised.
    :return: A string with the class name, function name, and exception.
    """

    # Get the current frame and extract the class name and function name
    frame = inspect.currentframe().f_back
    filename = inspect.getmodule(frame).__file__
    class_name = frame.f_locals.get('self', None).__class__.__name__
    function_name = frame.f_code.co_name

    # Construct the log string with the class name, function name, and exception
    log_string = f" {filename} | {class_name} Func({function_name}) | err-> {e} "

    log_string = '\033[91m' + log_string + '\033[0m'

    return log_string

def log_msg(msg: str):
    import inspect
    """
    Construct a log string with the class name, function name, and exception.

    :param e: The exception object that was raised.
    :return: A string with the class name, function name, and exception.
    """

    # Get the current frame and extract the class name and function name
    frame = inspect.currentframe().f_back
    filename = inspect.getmodule(frame).__file__
    class_name = frame.f_locals.get('self', None).__class__.__name__
    function_name = frame.f_code.co_name

    # Construct the log string with the class name, function name, and exception
    log_string = f" {filename} | {class_name} Func({function_name}) | MSG-> {msg} "

    log_string = '\033[32m' + log_string + '\033[0m'

    return log_string

