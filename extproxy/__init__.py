#!/usr/bin/env python
"""ExtProxy extend urllib2's ProxyHandler to support extra proxy types: HTTPS,
SOCKS. It provides a consistent user experience like HTTP proxy for the users.

This script is using a non-side-effects monkey patch, it did not applied to
build-in module socket, just inject some codes into `Request`, `ProxyHandler`,
`HTTPConnection`, `SSLContext` method's processing. No need to worry about
the patching, you can using everything like before, or you can unpatch it at
any time.

Usage:

    # Target can be imported before monkey patching
    from urllib.request import urlopen, build_opener, ProxyHandler


    # Import extproxy, auto apply monkey patching by `extproxy.patch_items`
    import extproxy


    # Use origin HTTP proxy
    proxy = "http://127.0.0.1:8080"


    # Use HTTPS proxy, use `set_https_proxy` to custom proxy's SSL verify mode
    import ssl
    proxy = "https://127.0.0.1:8443"

    cafile = "cafile path"
    set_https_proxy(proxy, check_hostname=False, cafile=cafile)

    context_settings = {
        "protocol": ssl.PROTOCOL_TLSv1_2,
        "cert_reqs": ssl.CERT_REQUIRED,  #
        "check_hostname": True,          #
        "cafile": "cafile path",         #
        "capath": "cafiles dir path",    #
        "cadata": b"ca data"             # Uesd to server auth
        "certfile": "certfile path",  #
        "keyfile": "keyfile path",    # Uesd to client auth
    }
    context = ssl._create_unverified_context(**context_settings)
     ...  # More custom settings
    set_https_proxy(proxy, context=context)


    # Use SOCKS proxy, `socks` can be: socks, socks4, socks4a, socks5, socks5h
    # SOCKS4 does not support remote resolving, but SOCKS4a/5 supported
    # 'socks' means SOCKS5, 'socks5h' means do not use remote resolving
    proxy = "socks://127.0.0.1:1080"


    # Set proxy via system/python environment variables
    import os
    os.environ["HTTP_PROXY"] = proxy
    os.environ["HTTPS_PROXY"] = proxy
    print(urlopen("https://httpbin.org/ip").read().decode())


    # Set proxy via ProxyHandler
    opener = build_opener(ProxyHandler({
        "http": proxy,
        "https": proxy
    }))
    print(opener.open("https://httpbin.org/ip").read().decode())


    # Restore monkey patch, then HTTPS, SOCKS proxy use can not continue working
    extproxy.restore_items()
"""

__version__ = "1.0.2"
__author__ = "SeaHOH<seahoh@gmail.com>"

from .extra import *

__all__ = ["__version__", "set_https_proxy", "patch_items", "restore_items"]

patch_items()
