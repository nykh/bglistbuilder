import requests
from defusedxml import ElementTree

class API(object):
    def __init__(self, root):
        sanitize_root = root.rstrip('/')
        self.root = sanitize_root

    def __getattr__(self, node):
        sanitized_node = node.rstrip('/')
        return API(self.root + '/' + sanitized_node)

    def __call__(self, *, _method="GET", **kwargs):
        res = requests.request(_method, url=self.root, params=kwargs)
        if res.status_code == 200:
            return self.postprocess(res.content)
        else:
            res.raise_for_status()

    @staticmethod
    def postprocess(content: str):
        return content

class XmlAPI(API):
    def __getattr__(self, node):
        sanitized_node = node.rstrip('/')
        return XmlAPI(self.root + '/' + sanitized_node)

    def __call__(self, *, _method="GET", **kwargs):
        return super(XmlAPI, self).__call__(_method=_method, **kwargs)

    @staticmethod
    def postprocess(content: str):
        parsed = ElementTree.fromstring(content)
        return parsed
