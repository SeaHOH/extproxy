"""Implement inet_pton and inet_ntop in python."""

import socket
from socket import error, AF_INET, AF_INET6, inet_aton, inet_ntoa
from struct import pack, unpack


try:
    _compat_str_types = (str, unicode)
    _compat_packed_types = (bytes, bytearray, unicode)
except NameError:
    _compat_str_types = (str, )
    _compat_packed_types = (bytes, bytearray)

def inet_pton(family, ip_string):
    if not isinstance(ip_string, _compat_str_types):
        raise TypeError("inet_pton() argument 2 must be string, not %s"
                        % type(ip_string).__name__)

    family = _int_family(family)
    try:
        if family == AF_INET:
        # inet_aton() also accepts strings like '1', '127.1', some also trailing
        # data like '127.0.0.1 whatever', but inet_pton() does not.
            ip_packed = inet_aton(ip_string)
            if inet_ntoa(ip_packed) == ip_string:
                # Only accept injective ip strings
                return ip_packed

        elif family == AF_INET6:
            parts = _explode_ip_string(ip_string).split(":")
            if len(parts) == 8:
                return pack("!8H", *[int(i, 16) for i in parts])
            else:
                ip4 = inet_aton(parts.pop())
                ip6 = pack("!6H", *[int(i, 16) for i in parts])
                return ip6 + ip4
    except:
        pass
    else:
        raise ValueError("unknown address family %s" % family)
    raise error("illegal IP address string passed to inet_pton")

def inet_ntop(family, ip_packed):
    es = None
    try:
        if not isinstance(ip_packed, _compat_packed_types):
            assert isinstance(ip_packed.decode("utf8"), _compat_str_types)
    except:
        es = "inet_ntop() argument 2 requires %sa bytes-like object, not %s" \
             % (bytes is str and "a string or " or "", type(ip_packed).__name__)
    if es:
        raise TypeError(es)

    family = _int_family(family)
    try:
        if family == AF_INET:
            return inet_ntoa(ip_packed)

        elif family == AF_INET6:
            hextets = ["%x" % i for i in unpack("!8H", ip_packed)]
            return ":".join(_compress_hextets(hextets))
    except:
        pass
    else:
        raise ValueError("unknown address family %s" % family)
    raise error("illegal IP address string passed to inet_pton")


def _int_family(family):
    try:
        return int(family)
    except:
        pass
    raise TypeError("%r object cannot be interpreted as an integer"
                    % type(family).__name__)

def _explode_ip_string(ip_string):
    if ip_string[:1] == "[":
        ip_string = ip_string[1:-1]
    assert 1 < len(ip_string) < 40
    if ip_string[:1] == ":":
        assert ip_string[:2] == "::"
        ip_string = "0" + ip_string
    if ip_string[-1:] == ":":
        assert ip_string[-2:] == "::"
        ip_string = ip_string + "0"

    d_clns = ip_string.count("::")
    assert d_clns == 0 or d_clns == 1 and ip_string.count(":::") == 0

    clns = ip_string.count(":")
    m_clns = 6 if "." in ip_string[-4:] else 7
    if d_clns:
        assert 1 < clns <= m_clns
        exploded = "0".join([":"] * (2 + m_clns - clns))
        ip_string = ip_string.replace("::", exploded, 1)
    else:
        assert clns == m_clns

    return ip_string

# Copy from ipaddress module
def _compress_hextets(hextets):
    best_doublecolon_start = -1
    best_doublecolon_len = 0
    doublecolon_start = -1
    doublecolon_len = 0
    for index, hextet in enumerate(hextets):
        if hextet == "0":
            doublecolon_len += 1
            if doublecolon_start == -1:
                # Start of a sequence of zeros.
                doublecolon_start = index
            if doublecolon_len > best_doublecolon_len:
                # This is the longest sequence of zeros so far.
                best_doublecolon_len = doublecolon_len
                best_doublecolon_start = doublecolon_start
        else:
            doublecolon_len = 0
            doublecolon_start = -1

    if best_doublecolon_len > 1:
        best_doublecolon_end = (best_doublecolon_start + best_doublecolon_len)
        # For zeros at the end of the address.
        if best_doublecolon_end == len(hextets):
            hextets += [""]
        hextets[best_doublecolon_start:best_doublecolon_end] = [""]
        # For zeros at the beginning of the address.
        if best_doublecolon_start == 0:
            hextets = [""] + hextets

    return hextets

if not hasattr(socket, "inet_pton"):
    socket.inet_pton = inet_pton

if not hasattr(socket, "inet_ntop"):
    socket.inet_ntop = inet_ntop
