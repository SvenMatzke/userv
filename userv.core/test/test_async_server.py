import pytest
import requests
import socket
from urllib3.util.connection import create_connection
@pytest.fixture()
def server():
    server = "s"
    yield server
    # shutdown server



def test_server(server):
    raise

def test_get_request(server):
    raise

def test_post_requets(server):
    raise

def test_serve_static(server):
    raise

def test_memory_useage(server):
    raise

def test_interrupted_request():
    # requests.get("http://192.168.2.50/index.html")
    sock = create_connection(('192.168.2.51', 80), socket_options=[(6, 1, 1)])
    sock.close()

