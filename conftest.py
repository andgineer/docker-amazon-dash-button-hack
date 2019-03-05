"""
Tests run from the project root folder.
But the code expects to run inside src folder.

So for tests we add src folder to sys.path.

This file is loaded first by py.test therefore we change sys.path for all other python files.
"""
import os.path
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
