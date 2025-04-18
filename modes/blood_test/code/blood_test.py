from mpf.core.mode import Mode

class BloodTest(Mode):

    def mode_start(self, **kwargs):
        self.log.info("Blood Test mode started")
        
        self.player.game_mode_active = True
        self.player.current_game_mode = "blood_test"
        self.player.phase1_complete = False
        self.player.phase2_complete = False

        # Register event handlers
        self.add_mode_event_handler('s_newton_opto_made_active', self._newton_shot_hit)
        self.add_mode_event_handler('newton_shots_complete', self._phase1_complete)

        self.add_mode_event_handler('s_blood_target_active', self._blood_target_hit)
        self.add_mode_event_handler('blood_target_hits_complete', self._phase2_complete)

        self.add_mode_event_handler('s_left_ramp_entry_1_active', self._left_ramp_hit)

        # Enable VUK
        self.machine.coils.c_mode_vuk.enable()

        self.machine.events.post('mode_objectives_update', text="MAKE 3 NEWTON BALL SHOTS!")

    def mode_stop(self, **kwargs):
        self.log.info("Blood Test mode stopped")

        self.machine.coils.c_mode_vuk.disable()
        self.player.game_mode_active = False
        self.player.current_game_mode = "none"

    def _newton_shot_hit(self, **kwargs):
        self.log.debug(f"Newton Shot Hit! Current newton shots: {self.player.newton_shots}")

    def _phase1_complete(self, **kwargs):
        self.log.info("Phase 1 complete: Newton hits done!")
        self.player.phase1_complete = True
        self.machine.events.post('mode_objectives_update', text="HIT BLOOD TARGET 4 TIMES!")

    def _blood_target_hit(self, **kwargs):
        self.log.debug(f"Blood Target Hit! Current blood target hits: {self.player.blood_target_hits}")

    def _phase2_complete(self, **kwargs):
        self.log.info("Phase 2 complete: Blood target hits done!")
        self.player.phase2_complete = True
        self.machine.events.post('mode_objectives_update', text="HIT LEFT RAMP TO COMPLETE!")
        self.machine.events.post('phase2_blood_test_ready_for_ramp')

#Handle the complete mode logic to end the mode
    def _left_ramp_hit(self, **kwargs):
        if self.player.phase1_complete and self.player.phase2_complete:
            self.log.info("Left Ramp hit after Phase 2. Completing Blood Test Mode.")
            self.machine.events.post('blood_test_complete')
