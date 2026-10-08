# -*- coding: utf-8 -*-
import weakref

import mod.client.extraClientApi as clientApi


ScreenNode = clientApi.GetScreenNodeCls()
ROOT = ('/variables_button_mappings_and_controls/safezone_screen_matrix'
        '/inner_matrix/safezone_screen_panel/root_screen_panel/cooldown')


class AttackCooldownUI(ScreenNode):
    """Render client module progress; the module alone owns the cooldown clock."""

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.module = weakref.proxy(param['module'])
        self._bar = None
        self._fill = None
        self._lastRender = None

    def Create(self):
        self._bar = self.GetBaseUIControl(ROOT + '/bar')
        self._fill = self._bar.asProgressBar()
        self._bar.SetVisible(False)
        self.module.OnUICreated(self)

    def Render(self, showBar, progress):
        state = (showBar, progress)
        if state == self._lastRender:
            return
        self._lastRender = state
        self._bar.SetVisible(showBar)
        if showBar:
            self._fill.SetValue(progress)

    def Destroy(self):
        self._bar = None
        self._fill = None
        self._lastRender = None
        self.module.OnUIDestroyed(self)
