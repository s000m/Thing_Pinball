from mpf.core.mode import Mode

class Infected(Mode):
    def mode_start(self, **kwargs):
        self.log.info("Infected mode started")
        # Set player variable indicating we're in this mode
        self.player.game_mode_active = True
        self.player.current_game_mode = "infected"
        self.player.phase1_complete = False
        self.player.left_ramp_hits = 0
        
        # Register handlers for left ramp
        self.add_mode_event_handler('s_left_ramp_entry_1_active', self._left_ramp_hit)
        
        # Register handlers for phase completion
        self.add_mode_event_handler('phase1_infected_complete', self._phase1_complete)
        self.add_mode_event_handler('s_3bank_tgt_d_active, s_3bank_tgt_o_active, s_3bank_tgt_g_active', self._dog_targets_hit)
        
        # Activate the VUK
        self.machine.coils.c_mode_vuk.enable()
        
        # Update display to inform player of objectives
        self.machine.events.post('mode_objectives_update', 
                               text="HIT LEFT RAMP 3 TIMES!")
        
    def mode_stop(self, **kwargs):
        self.log.info("Infected mode stopped")
        
        # Disable VUK
        self.machine.coils.c_mode_vuk.disable()
        
    def _left_ramp_hit(self, **kwargs):
        # Count is handled by the counter
        pass
        
    def _phase1_complete(self, **kwargs):
        self.log.info("Infected Phase 1 complete - Hit DOG targets to finish")
        self.player.phase1_complete = True
        
        # Update display to inform player of new objective
        self.machine.events.post('mode_objectives_update', 
                               text="COMPLETE DOG TARGETS TO FINISH INFECTED MODE!")
        
    def _dog_targets_hit(self, **kwargs):
        if self.player.phase1_complete:
            if (self.machine.switches.s_3bank_tgt_d.state and 
                self.machine.switches.s_3bank_tgt_o.state and 
                self.machine.switches.s_3bank_tgt_g.state):
                
                self.log.info("DOG targets complete after phase 1 - Completing infected mode")
                # Activate the drop target to reset the bank
                self.machine.coils.c_drop_target.pulse()
                # Complete the mode
                self.machine.events.post('infected_complete')
