import typing as t


class GenerationResult:
    def __init__(self, request_dict, response_dict):
        self.request_dict = request_dict
        self.response_dict = response_dict
        # self.__dict__.update(kwargs)

    def to_dict(self):
        return {
            "request_dict": self.request_dict,
            "response_dict": self.response_dict,
        }

    def from_dict(d: dict):
        return GenerationResult(d["request_dict"], d["response_dict"])
