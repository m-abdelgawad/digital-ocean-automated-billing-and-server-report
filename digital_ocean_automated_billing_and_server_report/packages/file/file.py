import os
import inspect


def caller_file_path():
    # Get absolute path of the caller module
    return inspect.stack()[1].filename


def caller_dir_path():
    # Get absolute path of the caller module
    caller_abs_path = inspect.stack()[1].filename
    return os.path.dirname(caller_abs_path)


def read(path):
    with open(path) as file:
        return file.read()


if __name__ == "__main__":
    print(caller_file_path())
