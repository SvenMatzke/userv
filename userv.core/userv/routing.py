from userv import HTTP_METHODS


class Router():

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
