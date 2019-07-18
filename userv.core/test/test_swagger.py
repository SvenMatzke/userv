from userv import swagger
from userv.routing import Router
from userv.swagger import _swagger_body
import json


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
    response = _swagger_body("tada", "title_", router_instance=router)
    str_response = "".join(response)
    read_dict = json.loads(str_response)
    assert '/resturl' in read_dict['paths'].keys()
