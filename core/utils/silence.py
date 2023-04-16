import os, sys
from contextlib import contextmanager

@contextmanager
def silence_function():
    """
    surpresses console output of a function called within the context manager
    """
    with open(os.devnull, "w") as devNull:
        initial = sys.stdout
        sys.stdout = devNull
        try: yield
        finally: sys.stdout = initial
