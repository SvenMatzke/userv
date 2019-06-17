The catch
=========
Simple async webserver

Webserver
=========
first we need to add routes to a router.
Atm creating json or text responses is part of the webserver but will be generalised to the core
in future.

First we add a server task to the event loop
Example:
::

    from userv.routing import Router
    from userv.async_server import App
    router = Router()

    web_server = App(router)
    web_server.run_task()


Now we have added the current app to the event loop and stll work on other tasks.
It will be run when we trigger the loop.run as all async tasks should.
