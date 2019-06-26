The catch
=========
Most simplistic socket server for micropython

Webserver
=========
first we need to add routes to a router. This is described in userv.core
although serving static files is described below.

Example:
::

    from userv.routing import Router
    from userv.socket_server import run_server
    router = Router()
    # we add some routes

    run_server(router)

this way the server starts and runs forever.
Because sometimes you want to start a standby mode there is way to kill the run task
by given a callback which controls the loop.
We call it the timeout callback for now. Basicly the server runs as
long as the function returns True.

Example:
::

    def we_never_timeout():
        return True

    run_server(router, timeout_callback=we_never_timeout)

This is only a realy simple and silly example, but be aware to not do heavy lifting in this function,
because it will hinder your server to react normal.
