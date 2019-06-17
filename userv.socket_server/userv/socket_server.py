import gc
import os
import socket
from userv import response_header, get_mime_type, parse_request

try:
    import ujson
except ImportError:
    import json


def text(writer, data, status=200, content_type="text/html", headers=None):
    writer.write(
        response_header(
            status=status,
            content_type=content_type,
            content_length=len(data),
            headers=headers
        )
    )
    writer.write(data)
    writer.write(b'\r\n')


def json(writer, data, status=200, headers=None):
    content_type = "application/json"
    try:
        data_string = ujson.dumps(data)
    except:
        text(
            writer,
            "cant decode data to json",
            status=422,
            headers=headers
        )
        return
    text(
        writer,
        data_string,
        status=status,
        content_type=content_type,
        headers=headers
    )


def static_file(writer, fname, buffer):
    if fname not in os.listdir():
        text(
            writer,
            "",
            status=404
        )
    else:
        mime_type = get_mime_type(fname)
        if mime_type is None:
            text(
                writer,
                "",
                status=415,
            )
            return
        # serve static file
        content_len = os.stat(fname)[6]
        buffer_size = len(buffer)
        writer.write(
            response_header(
                status=200,
                content_type=mime_type,
                content_length=content_len
            )
        )
        file_ptr = open(fname, "rb")
        for _ in range(0, (content_len // buffer_size)):
            file_ptr.readinto(buffer)
            writer.write(buffer)
            gc.collect()

        readed_len = file_ptr.readinto(buffer)
        writer.write(buffer[:readed_len])
        writer.write(b'\r\n')
        file_ptr.close()
        gc.collect()


class App:

    def __init__(self, router):
        """

        :type router: userv.routing.Router
        """
        self.router = router
        self._routes = dict()

    def read_buffered_request(self, reader):
        req = list()
        while True:
            line = reader.readline()
            req.append(line)
            if not line or line == b'\r\n':
                break
        return b"".join(req)

    def run(self, ip_address="0.0.0.0", port=80, timeout_callback=None):
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
                        self.run_handle(reader, writer)
                    finally:
                        reader.close()
                    writer.close()
                except Exception as e:
                    print(e)
        finally:
            # always close the socket
            s.close()
            gc.enable()

    def run_handle(self, reader, writer):
        complete_request = self.read_buffered_request(reader)
        gc.collect()
        parsed_request = parse_request(complete_request.decode())
        gc.collect()
        route = parsed_request.get('route')
        print("Serving ", route, " | ", parsed_request.get('method'))
        # routes
        callback = self.router.get(route=route, method=parsed_request.get('method'))
        gc.collect()
        if not callable(callback):
            text(writer, "Requested Route or method is not available", status=404)
        else:
            callback(writer, parsed_request)