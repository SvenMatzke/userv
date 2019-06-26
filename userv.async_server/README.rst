The catch
=========
Simple async webserver

Webserver
=========
First we need to add routes to a router. After this we can add a task to the
async loop with:

Example:
::

    from userv.routing import Router
    from userv.async_server import run_server
    router = Router()

    run_server(router)


Now we have added the current app to the event loop and we still have
to run the event loop.

Example:
::

    from uasyncio import get_event_loop
    loop = get_event_loop()
    loop.run_forever()

Now the server will run and serve your data.
