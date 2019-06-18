import os
import uasyncio as asyncio
from userv import response_header, get_mime_type, parse_request
from userv.routing import text

try:
    import ujson
except ImportError:
    import json


def _is_async_func(func):
    """
    returns if a func is async
    :rtype: bool
    """
    return isinstance(func, type(lambda: (yield)))


def run_server(router, address="0.0.0.0", port=80):
    """
    adds a task of an async server to the loop
    :type router: microroute.Router
    :type address: str
    :type port: int
    """

    def run_handle(self, reader, writer):
        print("started")
        complete_request = yield from reader.read()
        parsed_request = parse_request(complete_request.decode())
        route = parsed_request.get('route')
        if route.startswith('/static'):
            fname = route.split("/")[-1]
            if fname not in os.listdir():
                text_response = yield from text(
                    "File %s is not available " % fname,
                    status=404
                )
                yield from writer.awrite(
                    text_response
                )
            else:
                mime_type = get_mime_type(fname)
                if mime_type is None:
                    text_response = yield from text(
                        "",
                        status=415,
                    )
                    yield from writer.awrite(
                        text_response
                    )
                else:
                    # serve static file
                    yield from writer.awrite(
                        response_header(
                            status=200,
                            content_type=mime_type,
                            content_length=os.stat(fname)[0]
                        )
                    )
                    file_ptr = open(fname)
                    buf = bytearray(self._buffersize) # TODO
                    while True:
                        l = file_ptr.readinto(buf)
                        if not l:
                            break
                        yield from writer.awrite(buf, 0, l)
                    file_ptr.close()

        else:
            callback = yield from router.get(route=route, method=parsed_request.get('method'))
            if callback in [404, 405]:
                yield from text("Requested Route or method is not available", status=callback)
            response = yield from callback(parsed_request)
            yield from writer.awrite(
                response
            )
        yield from writer.aclose()

    loop = asyncio.get_event_loop()
    loop.call_soon(
        asyncio.start_server(run_handle, address, port)
    )
