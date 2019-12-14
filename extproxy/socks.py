"""Using PySocks to create and set new SOCKS proxy connection."""

import socket

from .compat import socks
from .util import is_ipv4


_socks4_no_rdns = set()

if socks is None:
    SOCKS_PROXY_TYPES = {
        "socks4" : None,
        "socks4a": None,
        "socks"  : None,
        "socks5" : None,
        "socks5h": None
    }
    def _set_tunnel_socks(self, proxy): pass

else:
    SOCKS_PROXY_TYPES = {
        "socks4" : (socks.PROXY_TYPE_SOCKS4, False),
        "socks4a": (socks.PROXY_TYPE_SOCKS4, True),
        "socks"  : (socks.PROXY_TYPE_SOCKS5, True),
        "socks5" : (socks.PROXY_TYPE_SOCKS5, True),
        "socks5h": (socks.PROXY_TYPE_SOCKS5, False)
    }

    def _set_tunnel_socks(self, proxy):
        proxy_type, proxy_rdns = SOCKS_PROXY_TYPES[proxy.scheme]
        proxy_kw = {
            "proxy_type": proxy_type,
            "proxy_addr": proxy.hostname,
            "proxy_port": proxy.port,
            "proxy_rdns": proxy_rdns,
            "proxy_username": proxy.username,
            "proxy_password": proxy.password
        }

        def create_connection(dest_pair, timeout=None, source_address=None,
                              proxy_kw=proxy_kw):
            host, port = dest_pair
            proxy_host = proxy_kw["proxy_addr"], proxy_kw["proxy_port"]
            if proxy_kw["proxy_rdns"]:
                proxy_kw["proxy_rdns"] = proxy_host not in _socks4_no_rdns
            rdns = proxy_kw["proxy_rdns"]
            socket_options = ((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1), )

            while True:
                try:
                    return socks.create_connection(
                            dest_pair, timeout, source_address,
                            socket_options=socket_options, **proxy_kw)
                except socks.SOCKS4Error as e:
                    if rdns and e.msg[:4] == "0x5b" and not is_ipv4(host):
                    # Maybe that SOCKS4 server doesn't support remote resolving
                    # Disable rdns and try again
                        proxy_kw["proxy_rdns"] = rdns = False
                        _socks4_no_rdns.add(proxy_host)
                    else:
                        raise e

        self._create_connection = create_connection
