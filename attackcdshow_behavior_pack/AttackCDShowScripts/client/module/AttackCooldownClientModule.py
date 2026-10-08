# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

from .BaseClientModule import BaseClientModule
from ...config.modConfig import ModName
from ...config.attackCooldown import (COOLDOWN_EVENT, UPDATE_RATE,
                                       UI_CLASS, UI_NAME, UI_SCREEN)
from ...util.listen import Listen


compFactory = clientApi.GetEngineCompFactory()


class AttackCooldownClientModule(BaseClientModule):
    """Own the server-triggered cooldown clock and expose its HUD progress."""

    def __init__(self, system):
        self._ui = None
        self._uiRegistered = False
        self._uiCreating = False
        self._destroyed = False
        self._cooldown = 0.0
        self._remaining = 0.0
        self._hudVisible = False
        BaseClientModule.__init__(self, system)
        self._view = compFactory.CreatePlayerView(self.playerId)

    def Update(self):
        if self._destroyed:
            return
        if self._remaining > 0.0:
            self._remaining = max(0.0, self._remaining - 1.0 / UPDATE_RATE)
            # Round-off at a tick boundary must not keep the bar one tick longer.
            if self._remaining < 1e-9:
                self._remaining = 0.0
        self._RefreshContext()
        self._Render()

    def _RefreshContext(self):
        if self._ui is None:
            return
        self._hudVisible = self._view.GetPerspective() == 0

    @Listen.server(COOLDOWN_EVENT)
    def OnCooldown(self, args):
        if self._destroyed:
            return
        self._cooldown = args['cooldown']
        self._remaining = self._cooldown
        self._RefreshContext()
        self._Render()

    @Listen.minecraft('UiInitFinished')
    def OnUiInitFinished(self, args):
        if self._destroyed:
            return
        if not self._uiRegistered:
            clientApi.RegisterUI(ModName, UI_NAME, UI_CLASS, UI_SCREEN)
            self._uiRegistered = True
        if self._ui is None and not self._uiCreating:
            self._uiCreating = True
            try:
                ui = clientApi.CreateUI(ModName, UI_NAME,
                                        {'isHud': 1, 'module': self})
                if ui is None and self._ui is None:
                    raise RuntimeError('AttackCooldown HUD creation failed')
            except Exception:
                self._uiCreating = False
                raise

    def OnUICreated(self, ui):
        if self._destroyed:
            return
        self._ui = ui
        self._uiCreating = False
        self._RefreshContext()
        self._Render()

    def OnUIDestroyed(self, ui):
        if self._ui is ui:
            self._ui = None
        self._uiCreating = False

    def _Render(self):
        if self._ui is None:
            return
        showBar = False
        progress = 0.0
        if self._hudVisible and self._cooldown > 0.0:
            if self._remaining > 0.0:
                showBar = True
                progress = max(0.0, min(1.0,
                                      1.0 - self._remaining / self._cooldown))
        self._ui.Render(showBar, progress)

    def Destroy(self):
        self._destroyed = True
        try:
            if self._ui is not None or self._uiCreating:
                clientApi.RemoveUI(ModName, UI_NAME)
        finally:
            self._ui = None
            self._uiCreating = False
            BaseClientModule.Destroy(self)
