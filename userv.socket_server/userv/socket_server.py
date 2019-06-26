import gc
import socket
from userv import parse_request
from userv.routing import text_response
import ulogging

_log = ulogging.getLogger("socket_server")
_log.setLevel(ulogging.DEBUG)


def _read_buffered_request(reader):
    req = list()
    while True:
        line = reader.readline()
        req.append(line)
        if not line or line == b'\r\n':
            break
    return b"".join(req)


def _run_handle(router, reader, writer):
    """
    run handle to serve data to the outside
    """
    complete_request = _read_buffered_request(reader)
    gc.collect()
    # TODO incomplete requests causes timeouts
    parsed_request = parse_request(complete_request.decode())
    gc.collect()
    route = parsed_request.get('route')
    _log.info("Serving %s | %s " % (route, parsed_request.get('method')))
    # routes
    callback = router.get(route=route, method=parsed_request.get('method'))
    gc.collect()
    router.get(route=route, method=parsed_request.get('method'))
    if callback in [404, 405]:
        _log.warning("Response with %s" % str(callback))
        generator = text_response("", status=callback)
    elif not callable(callback):
        _log.warning("Response with 404 Method is not callable.")
        generator = text_response("Method is not callable for given route", status=404)
    else:
        generator = callback(parsed_request)

    for line in generator:
        writer.write(line)


def run_server(router, ip_address="0.0.0.0", port=80, timeout_callback=None):
    """
    this method will handle the gc it self and so should your sites
    :param ip_address:
    :param port:
    :param timeout_callback: if None we run forever
    """
    addr = socket.getaddrinfo(ip_address, port)[0][-1]
    # creating socket mess
    s = socket.socket()
    gc.disable()
    s.bind(addr)
    _log.info("Server started at %s with port %s" % (ip_address, port))
    s.listen(1)
    timeout = lambda: True
    if timeout_callback is not None:
        timeout = timeout_callback
    try:
        while timeout():
            try:
                gc.collect()
                s.settimeout(60)
                writer, client_addr = s.accept()

                _log.info('client connected from: %s' % str(client_addr))
                # read request
                reader = writer.makefile('rwb', 0)

                try:
                    _run_handle(router, reader, writer)
                finally:
                    reader.close()
                writer.close()
            except Exception as e:
                _log.error(str(e))
    finally:
        # always close the socket
        s.close()
        gc.enable()
