# userv
Minimal webserver for micropython to lauch a socket webserver on esp8266.
For memory reasons on esp8266 we recommend to precompile userv with your firmware.

Sadly we cant go async because the memory is just not enough.

# setting up an Webserver and let it run
This will setup an app which can have urlpaths and run a server on 0.0.0.0 on port 80
```python
app = userv.App()
app.run_server()
```

# controlling a timeout after which the server will shutdown
Why do we want to shutdown the webserver. Lets say our esp runs on battery and we only want 
the server to online for a minute tops. Reasons for this can be i want to configure it or we need data for a 
few seconds but only on request. After your requests we want to go to deepsleep again.
For this to be happening we have a timeout_callback. 
When this function reaches False our server will be stoped with next timeout.

```python

def shutdown_reached():
    
    return # return False then shutdown should happen

app.run_server(
    timeout_callback=shutdown_reached)
```

# serve Static files
Having a webserver we might want to serve static files, like a need little 
configuration page.
To servee a static_file we need an bytearray which will be buffering our
file and serving it. The main purpose of this buffer is to control your memory.

```python

buffer = bytearray(1024)
def _index(writer, request):
    return userv.static_file(writer, "index.html", buffer)


def _static_js(writer, request):
    return userv.static_file(writer, "app.bundle.js", buffer)


def _static_css(writer, request):
    return userv.static_file(writer, "styles.bundle.css", buffer)

app.add_route("/", _index, method='GET')
app.add_route("/app.bundle.js", _static_js, method='GET')
app.add_route("/styles.bundle.css", _static_css, method='GET')

```

# serve text
Not much to say we need to serve data text is the simplest

```python
def _index(writer, request):
    return userv.text(writer, "hello")
```


# serve json data
Lets say we only want to serve and our webfrontend or so with json 

```python
 
def _get_settings(writer, request):
    return userv.json(writer, {"main": "hello"})


def _post_settings(writer, request):
    try:
        new_settings = ujson.loads(request.get('body'))
    except:
        return userv.json(writer, {"message": ""}, status=406)
    print(new_settings)
    return userv.json(writer, new_settings)

app.add_route("/settings", _get_settings, method='GET')
app.add_route("/settings", _post_settings, method='POST')

```
