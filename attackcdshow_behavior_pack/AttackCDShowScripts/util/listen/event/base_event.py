# -*- coding: utf-8 -*-
import json


class BaseEvent(object):

    @classmethod
    def load(cls, event=None):
        _instance = cls()
        if isinstance(event, dict):
            _instance.__dict__ = event
            return _instance
        return _instance

    @staticmethod
    def event_class_generator(target):
        for i in target.__subclasses__():
            yield i
            if i.__subclasses__():
                for d in BaseEvent.event_class_generator(i):
                    yield d

    @staticmethod
    def find_event_type(name):
        for i in BaseEvent.event_class_generator(BaseEvent):
            if i.__name__ == name:
                return i

    def dumps(self, **kwargs):
        return json.dumps({self.__class__.__name__: self.__dict__}, **kwargs)
