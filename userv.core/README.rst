The catch
=========
The first start for every webserver is routing and parsing html.
This is the core.


Routing
=======
Router objects are simple and are input to the server instances.
Example:
::

    from userv.routing import Router, text_response

    router = Router()

    def test(request):
        return text_response("some text")

    router.add("/resturl", test, method="GET")

you can get function test again with:
::

    router.get('/resturl', method="GET")


for creating swagger and so on there is a also a list command:
::

    router.list()

With these routes in one place we have full control even without
an server instance.

Response types
==============
There are a few build in response types text, json and static files.

The general gist of the response functions is to create a generator
which will be used to consumed by your server.

if you want to have full control about your memory flow or need to write a few
memory hungry responses feel free to write an response yourself.

Little hint make sure to use the response_header function and end the response with
an "\\r\\n".


Serve static files
==================
It is pretty simple just add the address with the file you want to serve.

Example:
::

    from userv.routing import static_file

    router.add("/index", static_file('boot.py'))

Although the example should never expose your code. It is a pretty simple and fast test.


Swagger your api
================
swagger.io is the a good way to document your api. This section is a quick way to serve an swagger.json
from your server. The view of this api has to be done in your local network.

Example for description:
::

    # Get requests have a parameter description
    @swagger.info("My_funny summary")
    @swagger.parameter('myvarname', description="", example='sdfs', required=True)
    @swagger.response(200, 'smth is off')
    def myrest_func(request):
        raise


    # Post request needs a body description
    @swagger.info("My_funny summary")
    @swagger.body('weatherinfo', {'tada': "examplevar",
                                  "tada2": 2})
    @swagger.response(200, 'smth is off')
    def post_myrest_func(request):
        raise

    router.add("/resturl", myrest_func, method="GET")
    router.add("/resturl", post_myrest_func, method="POST")



Example to serve swagger.json:
::

    from userv.swagger import swagger_file
    router.add(/swagger.json, swagger_file('my swagger api', "api title", router_instance=router))



Further packages & webserver
============================
Atm there is an implementation for an socketserver which runs even on on esp8266::

    pip install userv.socket_server

And an async server with an exchangable interface.::

    pip install userv.async_server


