The catch
=========
Most simplistic socket server for micropython

Webserver
=========
first we need to add routes to a router.
Atm creating json or text responses is part of the webserver but will be generalised to the core
in future.
Example:
::

    from userv.routing import Router
    from userv.socket_server import App
    router = Router()

    web_server = App(router)
    web_server.run()


server starts and runs forever.
Because sometimes you want to start a standby mode there is way to kill the run task
by given a callback which controls the loop.
We call it the timeout callback for now. Basicly the server runs as
long as the function returns True.

Example:
::

    def we_never_timeout():
        return True

    webserver.run(timeout_callback=we_never_timeout)

This is only a realy simple and silly example, but be aware to not do heavy lifting in this function,
because it will hinder your server to react normal.
