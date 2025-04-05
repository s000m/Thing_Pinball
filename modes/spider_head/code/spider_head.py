from mpf.core.mode import Mode

class SpiderHead(Mode):
    def mode_start(self, **kwargs):
        self.log.info("Spider Head mode started")
        # Set player variable indicating we're in this mode
        self.player.game_mode_active = True
        self.player.current_game_mode = "spider_head"
        self.player.phase1_complete = False
        self.player.spinner_hits = 0
        
        # Register handlers for Spinner
        self.add_mode_event_handler('s_spinner_active', self._spinner_hit)
        
        # Register handlers for phase completion
        self.add_mode_event_handler('phase1_spider_head_complete', self._phase1_complete)
        self.add_mode_event_handler('s_left_ramp_entry_1_active', self._left_ramp_hit)
        
        # Activate the VUK
        self.machine.coils.c_mode_vuk.enable()
        
        # Update display to inform player of objectives
        self.machine.events.post('mode_objectives_update', 
                               text="HIT SPINNER TO BURN HEAD!")
        
    def mode_stop(self, **kwargs):
        self.log.info("Spider Head mode stopped")
        
        # Disable VUK
        self.machine.coils.c_mode_vuk.disable()
        
    def _spinner_hit(self, **kwargs):
        # Count is handled by the counter
        pass
        
    def _phase1_complete(self, **kwargs):
        self.log.info("Spider Head Phase 1 complete - Hit Left Ramp to finish")
        self.player.phase1_complete = True
        
        # Update display to inform player of new objective
        self.machine.events.post('mode_objectives_update', 
                               text="HIT LEFT RAMP TO FINISH SPIDER HEAD MODE!")
        
    def _left_ramp_hit(self, **kwargs):
        if self.player.phase1_complete:
            self.log.info("Left ramp hit while phase 1 complete - Completing Spider Head mode")
            self.machine.events.post('spider_head_phase_2_complete')
