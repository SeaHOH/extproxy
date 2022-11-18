"""Using build-in module ssl to create and set new HTTPS proxy connection."""

import socket
import ssl

from .compat import urlparse


_https_proxy_contexts = {}

def set_https_proxy(proxy, check_hostname=None, cafile=None, context=None):
    """Used to set HTTPS proxy's SSL context.

    proxy
        A HTTPS proxy of string, eg: https://id:pw@127.0.0.1:8443
        The scheme name will be ignored.
    
    optional:

    check_hostname
        Whether to match the peer cert's hostname.
    cafile
        The path to a file of HTTPS proxy used CA cert in PEM format.
    context
        A `ssl.SSLContext` object, see the docs for more informations:
            https://docs.python.org/2/library/ssl.html#ssl-contexts
            https://docs.python.org/3/library/ssl.html#ssl-contexts
    """

    if not isinstance(proxy, tuple):
        proxy = urlparse(proxy)
    netloc = _get_normal_netloc(proxy)
    _https_proxy_contexts[netloc] = check_hostname, cafile, context

def _get_normal_netloc(proxy):
    if proxy.port is None:
        return proxy.netloc + ":443"
    else:
        return proxy.netloc

def _create_https_context(check_hostname, cafile, context):
    if context is None:
        context = ssl._create_default_https_context()
        # Enable PHA for TLS 1.3 connections if available
        if getattr(context, "post_handshake_auth", None) is not None:
            context.post_handshake_auth = True
    if cafile is not None:
        context.load_verify_locations(cafile)
    will_verify = context.verify_mode != ssl.CERT_NONE
    if check_hostname is None:
        check_hostname = context.check_hostname
    if check_hostname and not will_verify:
        raise ValueError("check_hostname needs a SSL context with "
                         "either CERT_OPTIONAL or CERT_REQUIRED")
    if check_hostname is not None:
        context.check_hostname = check_hostname
    return context

def _set_tunnel_https(self, proxy):
    def create_connection(dest_pair, timeout=None, source_address=None,
                          proxy=proxy):
        sock = socket.create_connection(dest_pair, timeout, source_address)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        netloc = _get_normal_netloc(proxy)
        context_parms = _https_proxy_contexts.get(netloc)
        if context_parms is None:
            context_parms = _https_proxy_contexts.get(netloc.rpartition("@")[-1])
        if context_parms is None:
            set_https_proxy(proxy)
            context_parms = _https_proxy_contexts[netloc]
        return _create_https_context(*context_parms).wrap_socket(
                    sock, server_hostname=proxy.hostname)

    self._create_connection = create_connection
