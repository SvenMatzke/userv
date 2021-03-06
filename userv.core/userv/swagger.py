"""
set attr on func does not work in micropython therefore we need a global store here
"""
from userv.routing import _file_response
from userv import set_default_header
import os

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
        parameters = old_data.get('parameters', [])
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
        old_data["parameters"] = parameters
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
        old_data['parameters'] = [parameters]

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
    try:
        information = _function_information.get(callback, {})
    except TypeError:
        information = {}
    information['summary'] = information.get('summary', "")
    information['description'] = information.get('summary', "")
    information['produces'] = information.get('produces', ["application/json"])
    information['consumes'] = information.get('consumes', ["application/json"])
    information['parameters'] = information.get("parameters", [])
    information['responses'] = information.get('responses', {})
    return information


def _swagger_body(info_description, title, version="1.0.0", host="127.0.0.1", base_path="/", router_instance=None):
    if router_instance is None:
        routes = {}
    else:
        routes = router_instance.routes()

    # infos
    yield "{"
    yield '"swagger": "2.0",'
    yield '"info": {'
    yield '"description": "%s",' % info_description
    yield '"version": "%s",' % version
    yield '"title": "%s"' % title
    yield '},'
    yield '"host": "%s",' % host
    yield '"basePath": "%s",' % base_path
    yield '"schemes": ["http"],'
    # paths
    yield '"paths": {'
    route_cout = len(routes)
    for idx, route in enumerate(routes.items()):
        yield '"%s": %s%s' % (
            route[0],
            json.dumps({method.lower(): _swagger_method(callback) for method, callback in route[1].items()}),
            "," if (idx + 1) < route_cout else ""
        )
    yield '},'
    # definitions
    yield '"definitions": {'
    definition_count = len(_definitions)
    for idx, definition in enumerate(_definitions.items()):
        yield '"%s": %s%s' % (
            definition[0],
            json.dumps(definition[1]),
            "," if (idx + 1) < definition_count else ""
        )
    yield '}'
    # end
    yield '}'


def swagger_file(info_description, title, swagger_file_name="swagger.json", version="1.0.0", host="127.0.0.1",
                 base_path="/", router_instance=None, headers=None):
    """
    :type info_description: str
    :type title: str
    :type swagger_file_name: str
    :type version: str
    :type host: str
    :type base_path: str
    :type router_instance: userv.routing.Router
    :type headers: list
    function to serve static files easily
    """
    # set default header for all responses
    # Parts of cors here
    default_header = [
        ("Access-Control-Allow-Headers", "Content-Type, api_key, Authorization"),
        ("Access-Control-Allow-Methods", "GET, POST, DELETE, PUT"),
        ("Access-Control-Allow-Origin", "*")
    ]
    set_default_header(default_header)
    # create swagger file
    if swagger_file_name in os.listdir():
        os.remove(swagger_file_name)
    file_ptr = open(swagger_file_name, "w")
    try:
        for line in _swagger_body(info_description, title, version, host, base_path, router_instance):
            file_ptr.write(line)
    finally:
        file_ptr.close()

    # serve swagger file
    def swagger_response(request):
        return _file_response("application/json", swagger_file_name, headers=headers)

    return swagger_response


def _swagger_index(url, title="Swagger UI"):
    """
    generator to create a proper swagger index url
    :type url: str
    :return: tuple
    """
    yield """<!-- HTML for static distribution bundle build -->"""
    yield """<!DOCTYPE html>"""
    yield """<html lang="en"><head><meta charset="UTF-8">"""
    yield """<title>%s</title>""" % title
    yield """<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.23.11/swagger-ui.css" >"""
    yield """<style>html{box-sizing: border-box;overflow: -moz-scrollbars-vertical;overflow-y: scroll;}*,"""
    yield """*:before,*:after"""
    yield """{box-sizing: inherit;}"""
    yield """body{margin:0;background: #fafafa;}</style></head>"""
    yield """<body><div id="swagger-ui"></div>"""
    yield """<script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.23.11/swagger-ui-bundle.js"> </script>"""
    yield """<script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.23.11/swagger-ui-standalone-preset.js"> </script>"""
    yield """<script>
    window.onload = function() {
        const ui = SwaggerUIBundle({
            url: "%s", dom_id: '#swagger-ui', deepLinking: true,
            presets: [SwaggerUIBundle.presets.apis,SwaggerUIStandalonePreset],
            plugins: [SwaggerUIBundle.plugins.DownloadUrl], layout: "StandaloneLayout"
          })
        window.ui = ui
    }</script></body></html>""" % url


def swagger_index(swagger_index_name="swagger_index.html", title="Swagger UI",
                  host="127.0.0.1", swagger_json_url="swagger.json", headers=None):
    """
    creates a proper swagger_index html
    :type swagger_index_name: str
    :type title: str
    :type host: str
    :type swagger_json_url: str
    :type headers: list
    """
    if swagger_index_name in os.listdir():
        os.remove(swagger_index_name)
    file_ptr = open(swagger_index_name, "w")
    try:
        for line in _swagger_index("http://%s/%s" % (host, swagger_json_url), title=title):
            file_ptr.write(line)
    finally:
        file_ptr.close()

    # serve swagger file
    def swagger_response(request):
        return _file_response("text/html", swagger_index_name, headers=headers)

    return swagger_response
