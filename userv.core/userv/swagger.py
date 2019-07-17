"""
set attr on func does not work in micropython therefore we need a global store here
"""
try:
    import ujson as json
except ImportError:
    import json

_function_information = dict()
_definitions = dict()


def _convert_to_swagger_type(value):
    """
    Every type has a swagger type
    :rtype: str
    """
    if isinstance(value, (str,)) or value is None:
        return "string"
    if isinstance(value, (float,)):
        return "number"
    if isinstance(value, (int,)):
        return "integer"
    if isinstance(value, (bool,)):
        return "boolean"
    if isinstance(value, (set, tuple, list)):
        return "array"
    if isinstance(value, (dict,)):
        return "object"
    return "string"


def _convert_dict_for_swagger(dict_instance):
    """
    converts all items from an dict
    :type dict_instance: dict
    :rtype: dict
    """
    converted_dict = {
        "type": "object",
        "properties": {}
    }
    for key, value in dict_instance.items():
        converted_type = _convert_to_swagger_type(value)
        if converted_type == "object":
            converted_dict["properties"][key] = _convert_dict_for_swagger(value)
        else:
            converted_dict["properties"][key] = {
                "type": _convert_to_swagger_type(value),
                "example": str(value)
            }
    return converted_dict


def info(summary, consumes=None, produces=None):
    """
    adds information to a function
    """

    def _wrap(func):
        old_data = _function_information.get(func, {})
        old_data["summary"] = summary
        if consumes is not None:
            old_data["consumes"] = consumes
        if produces is not None:
            old_data["produces"] = produces
        _function_information[func] = old_data
        return func

    return _wrap


def parameter(name, description="", example=None, required=False):
    """
    """

    def _wrap(func):
        old_data = _function_information.get(func, {})
        parameters = old_data.get('parameter', [])
        swagger_translation = {
            'in': 'query',
            'name': name,
            'description': description,
            'required': required,
            'type': _convert_to_swagger_type(example)
        }
        if example is not None:
            swagger_translation['example'] = example
        parameters.append(swagger_translation)
        old_data["parameter"] = parameters
        _function_information[func] = old_data
        return func

    return _wrap


def body(name, summary="", example=None):
    """
    adds an example body description
    """

    def _wrap(func):
        old_data = _function_information.get(func, {})
        parameters = {
            'name': "body",
            "in": "body",
            "description": summary,
            "required": True
        }
        if isinstance(example, dict):
            parameters['schema'] = {
                "$ref": "#/definitions/%s" % name
            }
            _definitions[name] = _convert_dict_for_swagger(example)
        else:
            parameters['example'] = _convert_to_swagger_type(example)
        old_data['parameter'] = [parameters]

        _function_information[func] = old_data
        return func

    return _wrap


def response(code, description=""):
    """
    adds a response to function
    """

    def _wrap(func):
        old_data = _function_information.get(func, {})
        responses = old_data.get('responses', {})
        responses[str(code)] = {'description': description}
        old_data['responses'] = responses
        _function_information[func] = old_data
        return func
    return _wrap


def _swagger_method(callback):
    """
    converts gathered information into swagger format
    """
    information = _function_information.get(callback, {})
    information['summary'] = information.get('summary', "")
    information['description'] = information.get('summary', "")
    information['produces'] = information.get('produces', ["application/json"])
    information['consumes'] = information.get('consumes', ["application/json"])
    information['parameters'] = information.get("parameters", [])
    information['responses'] = information.get('responses', {})
    return information


def swagger_response(info_description, title, version="1.0.0", host="127.0.0.1", base_path="/", router_instance=None):
    """
    :type info_description: str
    :type title: str
    :type version: str
    :type host: str
    :type base_path: str
    :type router_instance: userv.routing.Router
    :return:
    """
    if router_instance is None:
        routes = {}
    else:
        routes = router_instance.routes()
    # header

    # body
    # infos
    yield "{"
    yield '"swagger": "2.0",'
    yield '"info": {'
    yield '"description": "%s",' % info_description
    yield '"version": "%s",' % version
    yield '"title": "%s",' % title
    yield '},'
    yield '"host": "%s",' % host
    yield '"basePath": "%s",' % base_path
    yield '"schemes": ["http"],'

    # paths
    yield '"paths": {'
    for route, methods in routes.items():
        yield "%s: %s," % (
            route,
            json.dumps({method.lower(): json.dumps(_swagger_method(callback)) for method, callback in methods.items()})
        )
    yield '},'
    # definitions
    yield '"definitions": {'
    for definition_name, definition_data in _definitions.items():
        yield "%s: %s," % (
            definition_name,
            json.dumps(definition_data)
        )
    yield '}'
    # end
    yield '}'
