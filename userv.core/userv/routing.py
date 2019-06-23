from userv import HTTP_METHODS, response_header

try:
    import ujson as json
except ImportError:
    import json


def text_response(data, status=200, content_type="text/html", headers=None):
    """
    :type data: str | list
    :type status: int
    :type content_type: str
    :type headers: list
    :return: generator
    """
    if headers is None:
        headers = list()
    else:
        headers = list(headers)
    for line in response_header(
            status=status,
            content_type=content_type,
            content_length=len(data),
            headers=headers
    ):
        yield b"%s" % line
    if isinstance(data, (list, tuple, set)):
        for line in data:
            yield b"%s" % str(line).encode()
        yield b"\r\n"
    else:
        yield b"%s\r\n" % str(data).encode()


def json_response(data, status=200, headers=None):
    """
    casts the data container into an string and returns a complete response string
    """
    content_type = "application/json"
    try:
        data_string = json.dumps(data)
        gen = text_response(
            data_string,
            status=status,
            content_type=content_type,
            headers=headers
        )
    except:
        gen = text_response(
            "",
            status=422,
            headers=headers
        )

    for line in gen:
        yield line


class Router:

    def __init__(self):
        self._routes = dict()

    def add(self, route, callback, method='GET'):
        if method not in HTTP_METHODS:
            raise AttributeError("Method %s is not supported" % method)
        if route in self._routes:
            self._routes[route][method] = callback
        else:
            self._routes[route] = {method: callback}

    def get(self, route, method='GET'):
        """
        :type route: str
        :type method: str
        """
        if route.endswith("/"):
            route_with_slash = route
            route_without_slash = route[:-1]
        else:
            route_with_slash = route + "/"
            route_without_slash = route

        route_method_dict = self._routes.get(route_with_slash, self._routes.get(route_without_slash, None))
        if route_method_dict is None:
            return 404

        return route_method_dict.get(method, 405)

    def list(self):
        """gathers all information and returns a list of all urls"""
        for url, url_dict in self._routes.items():
            for method, callback in url_dict.items():
                yield {
                    'url': url,
                    'method': method,
                    'doc': callback.__doc__,
                }
