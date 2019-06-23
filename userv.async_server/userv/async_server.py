import uasyncio as asyncio
from userv import response_header, get_mime_type, parse_request
from userv.routing import text_response, json_response

#TODO
#Also writing tests
# def static_file(file_name):
#     def todo(request):
#         return ....  # TODO
# 
#     return todo
# if route.startswith('/static'):
#             fname = route.split("/")[-1]
#             if fname not in os.listdir():
#                 text_response = await text_response(
#                     "File %s is not available " % fname,
#                     status=404
#                 )
#                 await writer.awrite(
#                     text_response
#                 )
#             else:
#                 mime_type = get_mime_type(fname)
#                 if mime_type is None:
#                     text_response = await text_response(
#                         "",
#                         status=415,
#                     )
#                     await writer.awrite(
#                         text_response
#                     )
#                 else:
#                     # serve static file
#                     await writer.awrite(
#                         response_header(
#                             status=200,
#                             content_type=mime_type,
#                             content_length=os.stat(fname)[0]
#                         )
#                     )
#                     file_ptr = open(fname)
#                     buf = bytearray(self._buffersize) # TODO
#                     while True:
#                         l = file_ptr.readinto(buf)
#                         if not l:
#                             break
#                         await writer.awrite(buf, 0, l)
#                     file_ptr.close()
# 
#         else:

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

    async def run_handle(reader, writer): #TODO das ist doch nur ein request...
        print("started")
        complete_request = await reader.read()
        parsed_request = parse_request(complete_request.decode())
        route = parsed_request.get('route')
   
        callback = await router.get(route=route, method=parsed_request.get('method'))
        if callback in [404, 405]:
            response_generator = text_response("", status=callback)
        elif _is_async_func(callback):
            try:
                response_generator = await callback(parsed_request)
            except Exception as e:
                response_generator = text_response(str(e), status=500)
        else:
            try:
                response_generator = callback(parsed_request)
            except Exception as e:
                response_generator = text_response(str(e), status=500)

        for line in response_generator:
            await writer.awrite(line)
        await writer.aclose()

    loop = asyncio.get_event_loop()
    loop.call_soon(
        asyncio.start_server(run_handle, address, port)
    )
