"""
upload this file and test if everything runs need to translate all aspekts in tests
"""
import gc
print(gc.mem_free())
from async_server import run_server
from userv.routing import Router, text_response, static_file
from uasyncio import get_event_loop


async def smth(request):
    return text_response('ss')

r = Router()
r.add('/', lambda x: text_response('smth'))
r.add('/s', smth)
r.add('/file', static_file('socket_server.py'))
print(list(r.list()))
run_server(r)

loop = get_event_loop()

loop.run_forever()
print(gc.mem_free())