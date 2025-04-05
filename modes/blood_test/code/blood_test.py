from mpf.core.mode import Mode

class BloodTest(Mode):
    def mode_start(self, **kwargs):
        self.log.info("Blood Test mode started")
        # Set player variable indicating we're in this mode
        self.player.game_mode_active = True
        self.player.current_game_mode = "blood_test"
        self.player.phase1_complete = False
        self.player.newton_shots = 0
        
        # Register handlers for Newton Opto
        self.add_mode_event_handler('s_newton_opto_made_active', self._newton_shot_hit)
        
        # Register handlers for phase completion
        self.add_mode_event_handler('phase1_blood_test_complete', self._phase1_complete)
        self.add_mode_event_handler('s_left_ramp_entry_1_active', self._left_ramp_hit)
        
        # Activate the VUK
        self.machine.coils.c_mode_vuk.enable()
        
        # Update display to inform player of objectives
        self.machine.events.post('mode_objectives_update', 
                               text="MAKE 3 NEWTON BALL SHOTS!")
        
    def mode_stop(self, **kwargs):
        self.log.info("Blood Test mode stopped")
        
        # Disable VUK
        self.machine.coils.c_mode_vuk.disable()
        
    def _newton_shot_hit(self, **kwargs):
        # Count is handled by the counter
        pass
        
    def _phase1_complete(self, **kwargs):
        self.log.info("Blood Test Phase 1 complete - Hit Left Ramp to finish")
        self.player.phase1_complete = True
        
        # Update display to inform player of new objective
        self.machine.events.post('mode_objectives_update', 
                               text="HIT LEFT RAMP TO FINISH BLOOD TEST!")
        
    def _left_ramp_hit(self, **kwargs):
        if self.player.phase1_complete:
            self.log.info("Left ramp hit while phase 1 complete - Completing Blood Test mode")
            self.machine.events.post('blood_test_phase_2_complete')
