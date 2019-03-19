_status_lookup = (
    (200, b'OK'),
    (201, b'Created'),
    (202, b'Accepted'),
    (203, b'Non-Authoritative Information'),
    (204, b'No Content'),
    (205, b'Reset Content'),
    (206, b'Partial Content'),
    (207, b'Multi-Status'),
    (208, b'Already Reported'),
    (300, b'Multiple Choices'),
    (301, b'Moved Permanently'),
    (302, b'Found'),
    (303, b'See Other'),
    (304, b'Not Modified'),
    (305, b'Use Proxy'),
    (400, b'Bad Request'),
    (401, b'Unauthorized'),
    (403, b'Forbidden'),
    (404, b'Not Found'),
    (405, b'Method Not Allowed'),
    (406, b'Not Acceptable'),
    (407, b'Proxy Authentication Required'),
    (408, b'Request Timeout'),
    (409, b'Conflict'),
    (410, b'Gone'),
    (415, b'Unsupported Media Type'),
    (417, b'Expectation Failed'),
    (422, b'Unprocessable Entity'),
    (423, b'Locked'),
    (424, b'Failed Dependency'),
    (426, b'Upgrade Required'),
    (428, b'Precondition Required'),
    (429, b'Too Many Requests'),
    (431, b'Request Header Fields Too Large'),
    (500, b'Internal Server Error'),
    (501, b'Not Implemented'),
    (502, b'Bad Gateway'),
    (503, b'Service Unavailable'),
)


def _get_status_text(status_code):
    status_text_list = [text for code, text in _status_lookup if code == status_code]
    if len(status_text_list) == 0:
        return b"NA"
    return status_text_list[0]


def _get_mime_type(fname):
    # Provide minimal detection of important file
    # types to keep browsers happy
    if fname.endswith(".html"):
        return "text/html"
    if fname.endswith(".css"):
        return "text/css"
    if fname.endswith(".js"):
        return "text/javascript"
    if fname.endswith(".png") or fname.endswith(".jpg"):
        return "image"
    return None


def _render_headers(*args):
    content_str = b""
    for header, content in args:
        content_str += b"%s: %s\r\n" % (header, content)
    return content_str


def _response_header(status=200, content_type="text/html", content_length=None, headers=None):
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
                      _get_status_text(status),
                      _render_headers(*headers),
                  )
    return html_string


def _parse_header(list_of_header_str):
    header = dict()
    for header_str in list_of_header_str:
        key, value = header_str.split(":")[:2]
        header[key] = value
    return header


def _parse_request(request_string):
    heading, data = request_string.split("\r\n\r\n")[:2]
    header = heading.split("\r\n")
    data.rstrip("\r\n")
    method, route, http_version = header[0].split(" ")[:3]
    return dict(
        method=method,
        route=route,
        http_version=http_version,
        header=_parse_header(header[1:]),
        body=data.rstrip("\r\n")
    )