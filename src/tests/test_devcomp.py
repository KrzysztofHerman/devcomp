from devcomp import __version__
from devcomp import *

def test_version():
    assert __version__ == '0.0.1'

def test_csum():
    result = devcomp.csum(3,4)
    assert result == 7
