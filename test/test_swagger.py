from userv import swagger


@swagger.info("My_funny summary", consumes=[''], produces=[''])
@swagger.parameter('myvarname', description="", example='sdfs', required=True)
@swagger.body('weatherinfo', {'tada': "examplevar",
               "tada2": 2})
@swagger.response(200, 'smth is off')
def myrest_func(request):
    raise
