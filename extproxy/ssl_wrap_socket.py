"""Make build-in module ssl to wrap SSLSocket happy."""

from ssl import SSLSocket
from .util import forward_socket, socketpair


def _wrap_socket(self, sock, **kwargs):
    if isinstance(sock, SSLSocket):
        # SSLSocket() can not be wrapped twice, pipe to a new socket().
        # Whether to wait write/input data, because SSLSocket() has
        # no data available on SSL layer but readable on low layer
        # after do_handshake() with TLSv1.3.
        wait_local = sock.version() == "TLSv1.3" and sock.pending() == 0
        ssock, csock = socketpair()
        forward_socket(ssock, sock, wait_local=wait_local)
        sock = csock
    return _wrap_socket.orig(self, sock, **kwargs)
