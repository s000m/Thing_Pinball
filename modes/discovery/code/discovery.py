from mpf.core.mode import Mode

class Discovery(Mode):
    def mode_start(self, **kwargs):
        self.log.info("Discovery mode started")
        # Set player variable indicating we're in this mode
        self.player.game_mode_active = True
        self.player.current_game_mode = "discovery"
        self.player.phase1_complete = False
        
        # Register handlers for the pop bumpers
        self.add_mode_event_handler('s_pop_bumper_1_active', self._pop_bumper_hit)
        self.add_mode_event_handler('s_pop_bumper_2_active', self._pop_bumper_hit)
        self.add_mode_event_handler('s_pop_bumper_3_active', self._pop_bumper_hit)
        
        # Register handlers for phase completion
        self.add_mode_event_handler('phase1_discovery_complete', self._phase1_complete)
        self.add_mode_event_handler('s_left_ramp_entry_1_active', self._left_ramp_hit)
        
        # Activate the VUK
        self.machine.coils.c_mode_vuk.enable()
        
        # Update display to inform player of objectives
        self.machine.events.post('mode_objectives_update', 
                              text="HIT POP BUMPERS 100 TIMES!")
        
    def mode_stop(self, **kwargs):
        self.log.info("Discovery mode stopped")
        
        # Disable VUK
        self.machine.coils.c_mode_vuk.disable()
        
    def _pop_bumper_hit(self, **kwargs):
        # Already handled by the counter, but we could add additional logic here
        pass
        
    def _phase1_complete(self, **kwargs):
        self.log.info("Discovery Phase 1 complete - Hit Left Ramp to finish")
        self.player.phase1_complete = True
        
        # Update display to inform player of new objective
        self.machine.events.post('mode_objectives_update', 
                               text="HIT LEFT RAMP TO FINISH DISCOVERY!")
        
    def _left_ramp_hit(self, **kwargs):
        if self.player.phase1_complete:
            self.log.info("Left ramp hit while phase 1 complete - Completing discovery mode")
            self.machine.events.post('discovery_phase_2_complete')
