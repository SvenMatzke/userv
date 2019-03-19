import uasyncio as asyncio
import socket
import ujson
import os

STATUS_CODES = {
    100: b'Continue',
    101: b'Switching Protocols',
    102: b'Processing',
    200: b'OK',
    201: b'Created',
    202: b'Accepted',
    203: b'Non-Authoritative Information',
    204: b'No Content',
    205: b'Reset Content',
    206: b'Partial Content',
    207: b'Multi-Status',
    208: b'Already Reported',
    300: b'Multiple Choices',
    301: b'Moved Permanently',
    302: b'Found',
    303: b'See Other',
    304: b'Not Modified',
    305: b'Use Proxy',
    400: b'Bad Request',
    401: b'Unauthorized',
    403: b'Forbidden',
    404: b'Not Found',
    405: b'Method Not Allowed',
    406: b'Not Acceptable',
    407: b'Proxy Authentication Required',
    408: b'Request Timeout',
    409: b'Conflict',
    410: b'Gone',
    415: b'Unsupported Media Type',
    417: b'Expectation Failed',
    422: b'Unprocessable Entity',
    423: b'Locked',
    424: b'Failed Dependency',
    426: b'Upgrade Required',
    428: b'Precondition Required',
    429: b'Too Many Requests',
    431: b'Request Header Fields Too Large',
    500: b'Internal Server Error',
    501: b'Not Implemented',
    502: b'Bad Gateway',
    503: b'Service Unavailable',
    511: b'Network Authentication Required'
}
HTTP_METHODS = ('GET', 'POST', 'PUT', 'HEAD', 'OPTIONS', 'PATCH', 'DELETE')


def get_mime_type(fname):
    # Provide minimal detection of important file
    # types to keep browsers happy
    if fname.endswith(".html"):
        return "text/html"
    if fname.endswith(".css"):
        return "text/css"
    if fname.endswith(".png") or fname.endswith(".jpg"):
        return "image"
    return None


def _render_headers(*args):
    """

    :param args:
    :rtype: binary
    """
    content_str = b""
    for header, content in args:
        content_str += b"%s: %s\r\n" % (header, content)
    return content_str


# requests
def request(url, method="GET", body=None):
    """
    body has to be a seralized json string
    :type body: str
    :return: returns parsed response
    :rtype: dict
    """
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    headers = [
        ("Host", host),
        ("Accept", "%s;" % "application/json")
    ]
    if body is not None:
        headers.append(
            ("Content-Type", "%s; utf-8" % "application/json")
        )
        headers.append(
            ("Content-Length", str(len(body)))
        )
    request_string = b"%s %s HTTP/1.1\r\n" \
                     b"%s" \
                     b"\r\n"\
                     b"%s\r\n" % (
                         method,
                         path,
                         _render_headers(*headers),
                         "" if body is None else body.encode()
                     )
    s.send(request_string)
    complete_stream = b""
    while True:
        part_stream = s.recv(100)
        if part_stream:
            complete_stream += part_stream
        else:
            break
    s.close()
    parsed_reponse = _parse_response(complete_stream.decode())
    if "application/json" in parsed_reponse['header'].get('Content-Type', ""):
        parsed_reponse['body'] = ujson.loads(parsed_reponse.get("body", ""))
    return parsed_reponse


# Request parser
def _parse_header(list_of_header_str):
    header = dict()
    for header_str in list_of_header_str:
        key, value = header_str.split(":")
        header[key] = value
    return header


def parse_request(request_string):
    """
    Parses a request and splits them into an dict to return
    :param request_string: str
    :return: dict
    """
    heading, data = request_string.split("\r\n\r\n")
    header = heading.split("\r\n")
    data.rstrip("\r\n")
    method, route, http_version = header[0].split(" ")
    return dict(
        method=method,
        route=route,
        http_version=http_version,
        header=_parse_header(header[1:]),
        body=data.rstrip("\r\n")
    )


# Response part
def _response_header(status=200, content_type="text/html", content_length=None, headers=None):
    """
    :type status: int
    :type content_type: str
    :type headers: list
    :return: binary
    """

    if headers is None:
        headers = list()
    else:
        headers = list(headers)
    headers.append(("Content-Type", "%s; utf-8" % content_type))
    if content_length is not None:
        headers.append(("Content-Length", str(content_length)))
    html_string = b"HTTP/1.1 %i %s\r\n" \
                  b"%s" \
                  b"\r\n" % (
                      status,
                      STATUS_CODES.get(status, b"NA"),
                      _render_headers(*headers),
                  )
    return html_string

