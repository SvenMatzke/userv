The catch
=========

The frist start for every webserver is routing and parsing html.
This is the core.


Routing
=======
Router objects are simple and are input to the server instances.
Example:
::

    from userv.routing import Router, text

    router = Router()

    def test(request):
        return text("some text")

    router.add("/resturl", test, method="GET")

you can get function test again with:
::

    router.get('/resturl', method="GET")


for creating swagger and so on there is a also a list command:
::

    router.list()

With these object all server are instances and we have full controll even without
an server instance.

Response types
==============
There are a few build in response types text, json and static_files


Further packages & webserver
============================
Atm there is an implementation for an socketserver which runs even on on esp8266::

    pip install userv.socket_server

And an async server with the same interface.::

    pip install userv.async_server


