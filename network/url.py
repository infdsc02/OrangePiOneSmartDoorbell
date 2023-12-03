import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse
from json import JSONEncoder, JSONDecoder

from utils.stringutils import is_empty_string


@dataclass
class URL:
    protocol: str = "tcp"
    hostname: str = "localhost"
    port: int = 5555
    path: str = ""
    tls_cert_path: str = None

    def __str__(self):
        if is_empty_string(self.path):
            return "{}://{}:{}".format(self.protocol, self.hostname, self.port)
        else:
            return "{}://{}:{}/{}".format(self.protocol, self.hostname, self.port,
                                          self.path if self.path[0] != '/' else self.path[1:])

    def __repr__(self):
        return "URL[protocol = {}, hostname = {}, port = {}, path = {}]".format(self.protocol, self.hostname, self.port,
                                                                                self.path)

    def __hash__(self):
        return hash((self.protocol, self.hostname, self.port, self.path))


    @staticmethod
    def create_from_str(url_str: str):
        url = URL()
        parse_result = urlparse(url_str)
        url.protocol = parse_result.scheme
        url.hostname = parse_result.hostname
        url.port = parse_result.port
        url.path = parse_result.path
        return url

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.protocol == other.protocol and self.hostname == other.hostname and self.port == other.port and \
            self.path == other.path


class URLEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        url_dict = o.__dict__
        url_dict["__class__"] = "URL"
        return url_dict


class URLDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=URLDecoder.from_dict)

    @staticmethod
    def from_dict(d):
        if d.get("__class__") == "URL":
            return URL(protocol=d["protocol"], hostname=d["hostname"], port=d["port"], path=d["path"])
        return d

@dataclass
class BasicAuthURL(URL):
    user: str = ""
    passwd: str = ""

    def __str__(self):
        if is_empty_string(self.path):
            return "{}://{}:{}@{}:{}".format(self.protocol, self.user, self.passwd, self.hostname, self.port)
        else:
            return "{}://{}:{}@{}:{}/{}".format(self.protocol, self.user, self.passwd, self.hostname, self.port,
                                                self.path if self.path[0] != '/' else self.path[1:])

    def __repr__(self):
        return "BasicAuthURL[protocol = {}, hostname = {}, port = {}, path = {}, user = {}, " \
               "passwd = {}]".format(self.protocol, self.hostname, self.port, self.path, self.user, self.passwd)

    @staticmethod
    def create_from_str(url_str: str):
        url = BasicAuthURL()
        parse_result = urlparse(url_str)
        url.protocol = parse_result.scheme
        url.hostname = parse_result.hostname
        url.port = parse_result.port
        url.path = "{}?{}".format(parse_result.path, parse_result.query)
        url.user = parse_result.username
        url.passwd = parse_result.password
        return url

    def __eq__(self, other):
        return super().__eq__(other) and self.user == other.user and self.passwd == other.passwd


class BasicAuthURLEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        url_dict = o.__dict__
        url_dict["__class__"] = "BasicAuthURL"
        return url_dict


class BasicAuthURLDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=BasicAuthURLDecoder.from_dict)

    @staticmethod
    def from_dict(d):
        if d.get("__class__") == "BasicAuthURL":
            return BasicAuthURL(protocol=d["protocol"], hostname=d["hostname"], port=d["port"], path=d["path"],
                                user=d["user"], passwd=d["passwd"])
        return d
