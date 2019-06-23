import gc
import socket
from userv import response_header, get_mime_type, parse_request
from userv.routing import text_response


# TODO
# def static_file(writer, fname, buffer):
#     if fname not in os.listdir():
#         text(
#             writer,
#             "",
#             status=404
#         )
#     else:
#         mime_type = get_mime_type(fname)
#         if mime_type is None:
#             text(
#                 writer,
#                 "",
#                 status=415,
#             )
#             return
#         # serve static file
#         content_len = os.stat(fname)[6]
#         buffer_size = len(buffer)
#         writer.write(
#             response_header(
#                 status=200,
#                 content_type=mime_type,
#                 content_length=content_len
#             )
#         )
#         file_ptr = open(fname, "rb")
#         for _ in range(0, (content_len // buffer_size)):
#             file_ptr.readinto(buffer)
#             writer.write(buffer)
#             gc.collect()
#
#         readed_len = file_ptr.readinto(buffer)
#         writer.write(buffer[:readed_len])
#         writer.write(b'\r\n')
#         file_ptr.close()
#         gc.collect()


def _read_buffered_request(reader):
    req = list()
    while True:
        line = reader.readline()
        req.append(line)
        if not line or line == b'\r\n':
            break
    return b"".join(req)


def _run_handle(router, reader, writer):
    complete_request = _read_buffered_request(reader)
    gc.collect()
    parsed_request = parse_request(complete_request.decode())
    gc.collect()
    route = parsed_request.get('route')
    print("Serving ", route, " | ", parsed_request.get('method'))
    # routes
    callback = router.get(route=route, method=parsed_request.get('method'))
    gc.collect()
    if not callable(callback):
        generator = text_response("Requested Route or method is not available", status=404)
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
