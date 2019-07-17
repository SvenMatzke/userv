from userv import swagger
from userv.routing import Router
from userv.swagger import swagger_response


@swagger.info("My_funny summary")
@swagger.parameter('myvarname', description="", example='sdfs', required=True)
@swagger.response(200, 'smth is off')
def myrest_func(request):
    raise

@swagger.info("My_funny summary")
@swagger.body('weatherinfo', {'tada': "examplevar",
               "tada2": 2})
@swagger.response(200, 'smth is off')
def post_myrest_func(request):
    raise


router = Router()
router.add("/resturl", myrest_func, method="GET")
router.add("/resturl", post_myrest_func, method="POST")


def test_simple_sagger():
    response = swagger_response("tada", "title_", router_instance=router)
    str_response = "".join(response)
    print(str_response)
    assert str_response
    pass