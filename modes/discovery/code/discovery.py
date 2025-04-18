from mpf.core.mode import Mode

class Discovery(Mode):

    def mode_start(self, **kwargs):
        self.log.info("Discovery mode started")

        self.player.game_mode_active = True
        self.player.current_game_mode = "discovery"
        self.player.phase1_complete = False

        # Handlers
        self.add_mode_event_handler('s_pop_bumper_1_active', self._pop_bumper_hit)
        self.add_mode_event_handler('s_pop_bumper_2_active', self._pop_bumper_hit)
        self.add_mode_event_handler('s_pop_bumper_3_active', self._pop_bumper_hit)

        self.add_mode_event_handler('pop_bumper_value_complete', self._phase1_complete)
        self.add_mode_event_handler('s_left_ramp_entry_1_active', self._left_ramp_hit)

        # Enable VUK coil
        self.machine.coils.c_mode_vuk.enable()

        # Start instructions
        self.machine.events.post('mode_objectives_update', text="HIT 30 POP BUMPERS!")

    def mode_stop(self, **kwargs):
        self.log.info("Discovery mode stopped")

        self.machine.coils.c_mode_vuk.disable()
        self.player.game_mode_active = False
        self.player.current_game_mode = "none"

    def _pop_bumper_hit(self, **kwargs):
        self.log.debug(f"Pop Bumper Hit! Current value: {self.player.pop_bumper_value}")

    def _phase1_complete(self, **kwargs):
        self.log.info("Phase 1 complete: Pop Bumpers done!")
        self.player.phase1_complete = True

        # Update instructions
        self.machine.events.post('mode_objectives_update', text="HIT LEFT RAMP TO COMPLETE!")

    def _left_ramp_hit(self, **kwargs):
        if self.player.phase1_complete:
            self.log.info("Left Ramp hit during Phase 2. Completing Discovery Mode.")
            self.machine.events.post('discovery_complete')
