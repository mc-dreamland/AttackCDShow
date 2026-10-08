# -*- coding: utf-8 -*-
import weakref

import mod.client.extraClientApi as clientApi

from ...config.modConfig import *
from ...util.listen import Listen

compFactory = clientApi.GetEngineCompFactory()
engineName = clientApi.GetEngineNamespace()
engineSystem = clientApi.GetEngineSystemName()


class BaseClientModule(object):
    ListenDict = {Listen.minecraft: (engineName, engineSystem), Listen.client: (ModName, ClientSystemName), Listen.server: (ModName, ServerSystemName)}

    def __init__(self, system):
        if isinstance(system, weakref.ProxyTypes):
            self.system = system
        else:
            self.system = weakref.proxy(system)
        self.levelId = clientApi.GetLevelId()
        self.playerId = clientApi.GetLocalPlayerId()
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

    def NotifyToServer(self, eventName, eventData):
        return self.system.NotifyToServer(eventName, eventData)

    def CreateEngineSfx(self, path, pos=None, rot=None, scale=None):
        return self.system.CreateEngineSfx(path, pos=pos, rot=rot, scale=scale)

    def CreateEngineSfxFromEditor(self, path, pos=None, rot=None, scale=None):
        return self.system.CreateEngineSfxFromEditor(path, pos=pos, rot=rot, scale=scale)

    def CreateEngineParticle(self, path, pos):
        return self.system.CreateEngineParticle(path, pos)

    def CreateEngineEffectBind(self, path, bindEntity, aniName):
        return self.system.CreateEngineEffectBind(path, bindEntity, aniName)

    def DestroyEntity(self, entityId):
        return self.system.DestroyEntity(entityId)

    def BroadcastEvent(self, eventName, eventData):
        return self.system.BroadcastEvent(eventName, eventData)
   