# -*- coding: utf-8 -*-

from mod.common.mod import Mod
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
from .config.modConfig import *


@Mod.Binding(name=ModName, version=ModVersion)
class AttackCDShowMod(object):

    def __init__(self):
        pass

    @Mod.InitClient()
    def clientinit(self):
        clientApi.RegisterSystem(ModName, ClientSystemName, ClientSystemClsPath)

    @Mod.DestroyClient()
    def destroy_client(self):
        pass

    @Mod.DestroyServer()
    def destroy_server(self):
        pass
