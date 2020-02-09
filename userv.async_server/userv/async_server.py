import gc

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
from userv import parse_request
from userv.routing import text_response

try:
    import ulogging as logging
except ImportError:
    import logging

_log = logging.getLogger("async_server")
_log.setLevel(logging.DEBUG)


def _is_async_func(func):
    """
    returns if a func is a async function not a generator
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
    gc.collect()

    async def run_handle(reader, writer):
        """ every request will land here"""
        gc.collect()
        try:
            complete_request = await reader.read()  # possible Connection Error
            # TODO request not complete => parse error
            parsed_request = parse_request(complete_request.decode())
            route = parsed_request.get('route')
            _log.info("Serving %s | %s " % (route, parsed_request.get('method')))
            callback = router.get(route=route, method=parsed_request.get('method'))
        except Exception as e:
            callback = 500
            _log.error("Userv did not recieve proper request with error: %s" % str(e))
            response_generator = text_response("Error when recieving the request: " + str(e), status=500)

        if callback in [404, 405]:
            _log.warning("Response with %s" % callback)
            response_generator = text_response("", status=callback)
        elif callback in [500]:
            pass
        elif _is_async_func(callback):
            _log.info('async route')
            try:
                response_generator = await callback(parsed_request)
            except Exception as e:
                _log.error("Callback %s for route is async but was not executeable" % str(callback))
                response_generator = text_response(str(e), status=500)
        else:
            _log.info('normal route')
            try:
                response_generator = callback(parsed_request)
            except Exception as e:
                _log.error("Callback %s for route is normal function but was not executeable" % str(callback))
                response_generator = text_response(str(e), status=500)

        try:
            for line in response_generator:
                await writer.awrite(line)
            await writer.aclose()
        except Exception as e:
            _log.error("Writing to requester failed with: %s" % str(e))

    loop = asyncio.get_event_loop()
    loop.create_task(
        asyncio.start_server(run_handle, address, port)
    )
