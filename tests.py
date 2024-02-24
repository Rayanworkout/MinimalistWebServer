import pytest
import requests
import time

from MinimalistServer import MinimalistWebServer
from BaseServer.BaseServer import BaseServer


def test_default_port_number_is_correct():
    server = MinimalistWebServer()
    assert server.PORT == 8080

def test_default_host_is_correct():
    server = MinimalistWebServer()
    assert server.HOST == "127.0.0.1"
    
