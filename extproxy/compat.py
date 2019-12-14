"""Python version compatibility import."""

from __future__ import absolute_import, print_function

import sys

PY3 = sys.version_info.major == 3

def socks_warning():
    print("Pleaes install PySocks to support SOCKS proxy: "
          "`pip install PySocks`", file=sys.stderr)

try:
    import socks
except ImportError as e:
    if "win_inet_pton" in str(e):
        from . import socket_inet_p
        sys.modules['win_inet_pton'] = socket_inet_p
        import socks
    else:
        socks_warning()
        socks = None

try:
    from time import monotonic as time
except ImportError:
    from time import time

if PY3:
    from urllib.request import Request, ProxyHandler
    try:
        from urllib.request import splittype
    except ImportError:  # py38
        from urllib.request import _splittype as splittype
    from urllib.parse import urlparse
    from http.client import HTTPConnection
else:
    from urllib2 import Request, build_opener, ProxyHandler, splittype
    from urlparse import urlparse
    from httplib import HTTPConnection
