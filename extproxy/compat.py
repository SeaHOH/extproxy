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

if PY3:
    from urllib.request import Request, ProxyHandler, proxy_bypass
    try:
        from urllib.request import splittype
    except ImportError:  # py38
        from urllib.request import _splittype as splittype
    from urllib.parse import urlparse
    from http.client import HTTPConnection
    from time import perf_counter as mtime
else:
    from urllib2 import Request, ProxyHandler, proxy_bypass, splittype
    from urlparse import urlparse
    from httplib import HTTPConnection
    from time import time as mtime
