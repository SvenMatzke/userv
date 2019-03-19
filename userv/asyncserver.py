
async def text(data, status=200, content_type="text/html", headers=None):
    """
    :type data: str
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
    headers.append(("Content-Length", str(len(data))))
    html_string = b"%s" \
                  b"%s\r\n" % (
                      _response_header(
                          status=status,
                          content_type=content_type,
                          content_length=len(data),
                          headers=headers
                      ),
                      data
                  )
    return html_string


async def json(data, status=200, headers=None):
    """
    casts the data contrainer into an string and returns a complete response string
    """
    content_type = "application/json"
    try:
        data_string = ujson.dumps(data)
    except:
        return await text(
            "",
            status=422,
            headers=headers
        )
    return await text(
        data_string,
        status=status,
        content_type=content_type,
        headers=headers
    )


# reponse parser
def _parse_response(reponse_str):
    heading, data = reponse_str.split("\r\n\r\n")
    header = heading.split("\r\n")
    data.rstrip("\r\n")
    http_version, status_code, status_translation= header[0].split(" ")
    return dict(
        status_code=status_code,
        status_translation=status_translation,
        http_version=http_version,
        header=_parse_header(header[1:]),
        body=data.rstrip("\r\n")
    )

class App:

    def __init__(self):
        self._routes = dict()

    def add_route(self, route, callback, method='GET'):
        if method not in HTTP_METHODS:
            raise AttributeError("Method %s is not supported" % method)
        if route in self._routes:
            self._routes[route][method] = callback
        else:
            self._routes[route] = {method: callback}

    async def _get_callback(self, route, method):
        """
        :type route: str
        :type method: str
        """
        if route.endswith("/"):
            route_with_slash = route
            route_without_slash = route[:-1]
        else:
            route_with_slash = route + "/"
            route_without_slash = route

        route_method_dict = self._routes.get(route_with_slash, self._routes.get(route_without_slash, None))
        if route_method_dict is None:
            return 404

        return route_method_dict.get(method, 405)

    async def run_handle(self, reader, writer):
        complete_request = await reader.read()
        parsed_request = parse_request(complete_request.decode())
        route = parsed_request.get('route')
        if route.startswith('/static'):
            fname = route.split("/")[-1]
            if fname not in os.listdir():
                await writer.awrite(
                    await text(
                        "File %s is not available " % fname,
                        status=404
                    )
                )
            else:
                mime_type = get_mime_type(fname)
                if mime_type is None:
                    await writer.awrite(
                        await text(
                            "",
                            status=415,
                        )
                    )
                else:
                    # serve static file
                    await  writer.awrite(
                        _response_header(
                            status=200,
                            content_type=mime_type,
                            content_length=os.stat(fname)[0]
                        )
                    )
                    file_ptr = open(fname)
                    buf = bytearray(64)
                    while True:
                        l = file_ptr.readinto(buf)
                        if not l:
                            break
                        await writer.awrite(buf, 0, l)
                    file_ptr.close()

        else:
            callback = await self._get_callback(route=route, method=parsed_request.get('method'))
            if callback in [404, 405]:
                await text("Requested Route or method is not available", status=callback)
            response = await callback(parsed_request)
            await writer.awrite(
                response
            )
        await writer.aclose()
