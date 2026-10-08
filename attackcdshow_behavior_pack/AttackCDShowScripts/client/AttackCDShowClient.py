# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi

compFactory = clientApi.GetEngineCompFactory()
engineName = clientApi.GetEngineNamespace()
engineSystem = clientApi.GetEngineSystemName()


class AttackCDShowClient(clientApi.GetClientSystemCls()):
    def __init__(self, namespace, name):
        super(AttackCDShowClient, self).__init__(namespace, name)
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
        print "register client module:", module.__name__
        setattr(self, module.__name__, m)
        self._modules.append(m)

    def Setup(self):
        from .module.AttackCooldownClientModule import AttackCooldownClientModule
        self.register(AttackCooldownClientModule)
