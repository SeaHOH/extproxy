"""Some utility functions for extproxy."""

import socket
import select
import errno
import threading

from .compat import PY3, mtime


def _forward_socket(local, remote, wait_local=False,
                                   timeout=60, tick=4, bufsize=1024*32):
    buf = memoryview(bytearray(bufsize))
    maxpong = timeout
    allins = [local, remote]
    timecount = timeout
    try:
        if wait_local:
            r_timeout = local.gettimeout()
            if not r_timeout or r_timeout < timeout:
                local.settimeout(timeout)
            ndata = local.recv_into(buf)
            remote.sendall(buf[:ndata])

        while allins and timecount > 0:
            start_time = mtime()
            ins, _, err = select.select(allins, [], allins, tick)
            t = mtime() - start_time
            timecount -= int(t)
            if err:
                raise socket.error(err)
            for sock in ins:
                ndata = sock.recv_into(buf)
                if ndata:
                    other = local if sock is remote else remote
                    other.sendall(buf[:ndata])
                elif sock is remote:
                    return
                else:
                    allins.remove(sock)
            if ins and len(allins) == 2:
                timecount = max(min(timecount * 2, maxpong), tick)
    except Exception:
        pass
    finally:
        local.close()
        remote.close()

def forward_socket(*args, **kwargs):
    threading._start_new_thread(_forward_socket, args, kwargs)

try:
    socketpair = socket.socketpair
except AttributeError:
    # Origin: https://gist.github.com/4325783, by Geert Jansen.  Public domain.
    def socketpair(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
        if family == socket.AF_INET:
            host = "127.0.0.1"
        elif family == socket.AF_INET6:
            host = "::1"
        else:
            raise ValueError("Only AF_INET and AF_INET6 socket address families"
                             " are supported")
        if type != socket.SOCK_STREAM:
            raise ValueError("Only SOCK_STREAM socket type is supported")
        if proto != 0:
            raise ValueError("Only protocol zero is supported")

        # We create a connected TCP socket. Note the trick with
        # setblocking(False) that prevents us from having to create a thread.
        lsock = socket.socket(family, type, proto)
        try:
            lsock.bind((host, 0))
            lsock.listen(1)
            # On IPv6, ignore flow_info and scope_id
            addr, port = lsock.getsockname()[:2]
            csock = socket.socket(family, type, proto)
            try:
                csock.setblocking(False)
                if PY3:
                    try:
                        csock.connect((addr, port))
                    except (BlockingIOError, InterruptedError):
                        pass
                else:
                    try:
                        csock.connect((addr, port))
                    except socket.error as e:
                        if e.errno != errno.WSAEWOULDBLOCK:
                            raise
                csock.setblocking(True)
                ssock, _ = lsock.accept()
            except:
                csock.close()
                raise
        finally:
            lsock.close()
        return (ssock, csock)

def is_ipv4(s):
    try:
        socket.inet_pton(socket.AF_INET, s)
    except:
        return False
    else:
        return True
