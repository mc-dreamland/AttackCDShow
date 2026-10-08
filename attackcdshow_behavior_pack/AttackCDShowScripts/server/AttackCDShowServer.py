# -*- coding: utf-8 -*-
import mod.server.extraServerApi as serverApi

compFactory = serverApi.GetEngineCompFactory()
engineName = serverApi.GetEngineNamespace()
engineSystem = serverApi.GetEngineSystemName()


class AttackCDShowServer(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, name):
        super(AttackCDShowServer, self).__init__(namespace, name)
        self._modules = []
        self.Setup()

    def Update(self):
        for m in self._modules:
            m.Update()

    def Destroy(self):
        for m in self._modules:
            try:
                m.Destroy()
            except:
                print "destory", m.__class__.__name__, "fail"

        # for listened in self.listenEvents:
        #     namespace, systemName, eventName, instance, func, priority = listened.namespace, listened.systemName, listened.eventName, listened.instance, listened.funcName, listened.priority
        #     self.UnListenForEvent(namespace, systemName, eventName, instance, func, priority)

    def register(self, module):
        m = module(self)
        print "register server module:", module.__name__
        setattr(self, module.__name__, m)
        self._modules.append(m)

    def Setup(self):
        from .module.AttackCooldownServerModule import AttackCooldownServerModule
        self.register(AttackCooldownServerModule)
