# -*- coding: utf-8 -*-
import math

import mod.server.extraServerApi as serverApi

from .BaseServerModule import BaseServerModule
from ...config.attackCooldown import COOLDOWN_EVENT


class AttackCooldownServerModule(BaseServerModule):
    """Send explicit display durations without tracking combat or cooldown state."""

    def _IsOnlinePlayer(self, playerId):
        return isinstance(playerId, basestring) and playerId in serverApi.GetPlayerList()

    def StartCooldown(self, playerId, cooldownSeconds):
        """Send a finite nonnegative duration to an online player's client.

        Zero clears the display. Invalid durations raise ValueError; offline
        players return False. Access through AttackCooldownServerModule on the
        server system.
        """
        if isinstance(cooldownSeconds, bool) or not isinstance(cooldownSeconds, (int, long, float)):
            raise ValueError("cooldownSeconds must be a finite nonnegative number")
        try:
            cooldownSeconds = float(cooldownSeconds)
        except OverflowError:
            raise ValueError("cooldownSeconds must be a finite nonnegative number")
        if cooldownSeconds < 0.0 or math.isnan(cooldownSeconds) or math.isinf(cooldownSeconds):
            raise ValueError("cooldownSeconds must be a finite nonnegative number")
        if not self._IsOnlinePlayer(playerId):
            return False
        self.NotifyToClient(playerId, COOLDOWN_EVENT, {"cooldown": cooldownSeconds})
        return True
