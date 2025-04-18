from mpf.core.mode import Mode

class SpiderHead(Mode):

    def mode_start(self, **kwargs):
        self.log.info("Spider Head mode started")

        self.player.game_mode_active = True
        self.player.current_game_mode = "spider_head"
        self.player.phase1_complete = False

        # Handlers
        self.add_mode_event_handler('s_spinner_active', self._spinner_hit)
        self.add_mode_event_handler('spinner_complete_spider', self._phase1_complete)
        self.add_mode_event_handler('s_left_ramp_entry_1_active', self._left_ramp_hit)

        # Enable VUK
        self.machine.coils.c_mode_vuk.enable()

        self.machine.events.post('mode_objectives_update', text="HIT SPINNER TO BURN HEAD!")

    def mode_stop(self, **kwargs):
        self.log.info("Spider Head mode stopped")

        self.machine.coils.c_mode_vuk.disable()
        self.player.game_mode_active = False
        self.player.current_game_mode = "none"

    def _spinner_hit(self, **kwargs):
        self.log.debug(f"Spinner Hit! Current spinner hits: {self.player.spinner_hits}")

    def _phase1_complete(self, **kwargs):
        self.log.info("Phase 1 complete: Spinner hits done!")
        self.player.phase1_complete = True
        self.machine.events.post('mode_objectives_update', text="HIT LEFT RAMP TO COMPLETE!")

    def _left_ramp_hit(self, **kwargs):
        if self.player.phase1_complete:
            self.log.info("Left Ramp hit after Phase 1. Completing Spider Head Mode.")
            self.machine.events.post('spider_head_complete')
