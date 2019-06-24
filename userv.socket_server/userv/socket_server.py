import gc
import socket
import os
from userv import response_header, get_mime_type, parse_request
from userv.routing import text_response
import ulogging


def _file_response(mime_type, file_name, headers=None):
    content_len = os.stat(file_name)[6]
    for line in response_header(
            status=200,
            content_type=mime_type,
            content_length=content_len,
            headers=headers
    ):
        yield b"%s" % line
    buffer = bytearray(128)
    buffer_size = len(buffer)
    file_ptr = open(file_name, "rb")
    for _ in range(0, (content_len // buffer_size)):
        file_ptr.readinto(buffer)
        yield bytes(buffer)

    readed_len = file_ptr.readinto(buffer)
    file_ptr.close()
    gc.collect()
    yield bytes(buffer[:readed_len])
    yield b"\r\n"


def static_file(file_name):
    """
    function to serve static files easily
    """

    def file_response(request):
        if file_name not in os.listdir():
            return text_response("", status=404)
        else:
            mime_type = get_mime_type(file_name)
            return _file_response(mime_type, file_name)

    return file_response


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
    parsed_request = parse_request(complete_request.decode())
    gc.collect()
    route = parsed_request.get('route')
    print("Serving ", route, " | ", parsed_request.get('method'))
    # routes
    callback = router.get(route=route, method=parsed_request.get('method'))
    gc.collect()
    router.get(route=route, method=parsed_request.get('method'))
    if callback in [404, 405]:
        generator = text_response("", status=callback)
    elif not callable(callback):
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
    # add some basic logging
    log = ulogging.getLogger("socket_server")
    log.setLevel(ulogging.DEBUG)

    # creating socket mess
    s = socket.socket()
    gc.disable()
    s.bind(addr)
    print("Server started at %s with port %s" % (ip_address, port))
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

                print('client connected from: ', client_addr)
                # read request
                reader = writer.makefile('rwb', 0)

                try:
                    _run_handle(router, reader, writer)
                finally:
                    reader.close()
                writer.close()
            except Exception as e:
                print(e)
    finally:
        # always close the socket
        s.close()
        gc.enable()
