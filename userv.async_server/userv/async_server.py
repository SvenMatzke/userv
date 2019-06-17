import os
from asyncio import get_event_loop
from userv import response_header, get_mime_type, parse_request, parse_header

try:
    import ujson
except ImportError:
    import json


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
                      response_header(
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
    http_version, status_code, status_translation = header[0].split(" ")
    return dict(
        status_code=status_code,
        status_translation=status_translation,
        http_version=http_version,
        header=parse_header(header[1:]),
        body=data.rstrip("\r\n")
    )


class App:

    def __init__(self, router, buffersize=64):
        """

        :type router: microroute.Router
        """
        self.router = router
        self._buffersize = buffersize
        self._routes = dict()

    def run_task(self, address="0.0.0.0", port=80):
        """
        adds a run task to the current eventloop.
        therefore server will start as soon as async.run is called
        :param address:
        :param port:
        :return:
        """
        loop = get_event_loop()
        loop.create_task(
            loop.start_server(self._run_handle, address, port)
        )

    async def _run_handle(self, reader, writer):
        print("started")
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
                        response_header(
                            status=200,
                            content_type=mime_type,
                            content_length=os.stat(fname)[0]
                        )
                    )
                    file_ptr = open(fname)
                    buf = bytearray(self._buffersize)
                    while True:
                        l = file_ptr.readinto(buf)
                        if not l:
                            break
                        await writer.awrite(buf, 0, l)
                    file_ptr.close()

        else:
            callback = await self.router.get(route=route, method=parsed_request.get('method'))
            if callback in [404, 405]:
                await text("Requested Route or method is not available", status=callback)
            response = await callback(parsed_request)
            await writer.awrite(
                response
            )
        await writer.aclose()

