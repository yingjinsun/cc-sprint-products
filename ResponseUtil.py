from ConstantUtil import Constant
class Response(object):

    def __init__(self):
        self.response = dict()

    def success(self, data):
        self.response["code"] = Constant().OK
        self.response["message"] = "success"
        self.response["data"] = data
        return self.response

    def failed(self):
        self.response["code"] = Constant().NOT_FOUND
        self.response["message"] = "failed"
        return self.response

    def resp(self, code, data):
        self.response["code"] = code
        self.response["message"] = None
        self.response["data"] = data
        return self.response