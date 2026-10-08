# -*- coding: utf-8 -*-
import weakref
from copy import deepcopy

import mod.server.extraServerApi as serverApi
from mod.common.minecraftEnum import ItemPosType

from ...config.modConfig import *
from ...util.listen import Listen

compFactory = serverApi.GetEngineCompFactory()
engineName = serverApi.GetEngineNamespace()
engineSystem = serverApi.GetEngineSystemName()


class BaseServerModule(object):
    ListenDict = {Listen.minecraft: (engineName, engineSystem), Listen.client: (ModName, ClientSystemName), Listen.server: (ModName, ServerSystemName)}

    def __init__(self, system):
        if isinstance(system, weakref.ProxyTypes):
            self.system = system
        else:
            self.system = weakref.proxy(system)
        self.levelId = serverApi.GetLevelId()
        self.__listened_events = []
        self.onRegister()

    def onRegister(self):
        for key in dir(self):
            obj = getattr(self, key)
            if callable(obj) and hasattr(obj, 'listen_event'):
                event = getattr(obj, "listen_event")
                _type = getattr(obj, "listen_type")
                priority = getattr(obj, "listen_priority")
                self.listen(event, obj, _type=_type, priority=priority)

    def Update(self):
        pass

    def Destroy(self):
        self.Disable()

    def Disable(self):
        for name, system, event, instance, func, priority in self.__listened_events[:]:
            self.UnListenForEvent(name, system, event, instance, func, priority)

    def ListenForEvent(self, name, system, event, instance, func, priority=0):
        self.__listened_events.append((name, system, event, instance, func, priority))
        self.system.ListenForEvent(name, system, event, instance, func, priority=priority)

    def UnListenForEvent(self, name, system, event, instance, func, priority=0):
        self.__listened_events.remove((name, system, event, instance, func, priority))
        self.system.UnListenForEvent(name, system, event, instance, func, priority=priority)

    def listen(self, event, func, _type=Listen.minecraft, priority=0):
        if _type not in self.ListenDict:
            return
        name, system = self.ListenDict[_type]
        self.ListenForEvent(name, system, event, self, func, priority=priority)

    def unlisten(self, event, func, _type=Listen.minecraft, priority=0):
        if _type not in self.ListenDict:
            return
        name, system = self.ListenDict[_type]
        self.UnListenForEvent(name, system, event, self, func, priority=priority)

    def BroadcastToAllClient(self, eventName, eventData):
        return self.system.BroadcastToAllClient(eventName, eventData)

    def BroadcastEvent(self, eventName, eventData):
        return self.system.BroadcastEvent(eventName, eventData)

    def NotifyToClient(self, targetId, eventName, eventData):
        return self.system.NotifyToClient(targetId, eventName, eventData)

    def CreateEngineEntityByTypeStr(self, engineTypeStr, pos, rot, dimensionId=0, isNpc=False):
        return self.system.CreateEngineEntityByTypeStr(engineTypeStr, pos, rot, dimensionId=dimensionId, isNpc=isNpc)

    def CreateEngineItemEntity(self, itemDict, dimensionId=0, pos=(0, 0, 0)):
        return self.system.CreateEngineItemEntity(itemDict, dimensionId=dimensionId, pos=pos)

    def DestroyEntity(self, entityId):
        return self.system.DestroyEntity(entityId)