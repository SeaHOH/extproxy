#!/usr/bin/env python
"""Monkey patching build-in modules to support extra proxy types."""

from .compat import (socks_warning, proxy_bypass, splittype, urlparse,
                     Request, ProxyHandler, HTTPConnection)
from .https import set_https_proxy, _set_tunnel_https
from .socks import SOCKS_PROXY_TYPES, _set_tunnel_socks
from .ssl_wrap_socket import _wrap_socket
from ssl import SSLContext


__all__ = ["set_https_proxy", "patch_items", "restore_items"]

def _set_proxy(self, host, type):
    if ":/" in host:
        self._tunnel_host = host, type, self._tunnel_host
    else:
        _set_proxy.orig(self, host, type)

def _proxy_open(self, req, proxy, type):
    if req.host and proxy_bypass(req.host):
        return

    proxy_type = splittype(proxy)[0]

    if proxy_type == "https":
        _proxy = "http" + proxy[5:]                #
        _proxy_open.orig(self, req, _proxy, type)  # HTTP proxy setting
        req.set_proxy(proxy, "https")
        return

    if proxy_type in SOCKS_PROXY_TYPES:
        if SOCKS_PROXY_TYPES[proxy_type] is None:
            socks_warning()
        else:
            req.set_proxy(proxy, "socks")
            return

    return _proxy_open.orig(self, req, proxy, type)

def _set_tunnel(self, host, port=None, headers=None):
    try:
        proxy, type, tunnel_host = host
    except ValueError:
        _set_tunnel.orig(self, host, port, headers)
        return
    if self.sock:
        raise RuntimeError("Can't set up tunnel for established connection")

    proxy = urlparse(proxy)
    if type == "https":
        _set_tunnel_https(self, proxy)
    elif type == "socks":
        _set_tunnel_socks(self, proxy)

    if tunnel_host:
        # Go on setting the HTTP tunnel, if need
        _set_tunnel.orig(self, tunnel_host, port, headers)

_items_to_patch = (
    (Request,         "set_proxy",   _set_proxy),
    (ProxyHandler,    "proxy_open",  _proxy_open),
    (HTTPConnection,  "set_tunnel",  _set_tunnel),
    (SSLContext,      "wrap_socket", _wrap_socket)
)

def patch_items():
    """Apply monkey patch"""
    for obj, name, new_value in _items_to_patch:
        old_value = getattr(obj, name)
        # py2 get unbound function
        if getattr(old_value, "im_func", old_value) is new_value:
            continue
        setattr(new_value, "orig", old_value)
        setattr(obj, name, new_value)

def restore_items():
    """Restore monkey patch"""
    for obj, name, new_value in _items_to_patch:
        old_value = getattr(new_value, "orig", None)
        if old_value is None:
            continue
        delattr(new_value, "orig")
        setattr(obj, name, old_value)
