from userv.routing import Router, text_response, json_response


def test_add_and_get_routes():
    router = Router()

    # urls should be unique on url +method!

    def test():
        pass

    router.add("/resturl", test, method="GET")
    assert test == router.get('/resturl', method="GET")


def test_get_unknown_route():
    router = Router()

    assert router.get("/resturl") == 404


def test_get_unknown_method():
    router = Router()

    def test():
        pass

    router.add("/resturl", test, method="POST")

    assert router.get("/resturl") == 405


def test_route_listings():
    router = Router()

    def test():
        """testing info"""
        pass

    router.add("/geturl", test, method="POST")

    swagger_info = list(router.list())
    assert len(swagger_info) == 1
    assert swagger_info[0]['url'] == "/geturl"
    assert swagger_info[0]['method'] == "POST"
    assert swagger_info[0]['doc'] == "testing info"


def test_text_func():
    text_gen = text_response("hiho")
    msg = list(text_gen)
    assert len(msg) == 5
    assert "hiho" in msg[-1].decode()
    assert "text/html" in msg[1].decode()


def test_json_func():
    json_gen = json_response({"tada": "hiho"})
    msg = list(json_gen)
    assert len(msg) == 5
    assert "hiho" in msg[-1].decode()
    assert "application/json" in msg[1].decode()
