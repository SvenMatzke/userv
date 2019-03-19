import os

if os.uname().sysname in ('esp8266', ):
    # lower memory usage
    from userv.socketserver import App, text, json, static_file
else:
    # higher memory usage
    from userv.asyncserver import App, text, json


