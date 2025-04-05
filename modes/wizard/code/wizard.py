from mpf.core.mode import Mode

class Wizard(Mode):
    def mode_start(self, **kwargs):
        self.log.info("Wizard mode started")
        # Set player variable indicating we're in this mode
        self.player.game_mode_active = True
        self.player.current_game_mode = "wizard"
        self.player.phase1_complete = False
        self.player.pop_bumper_wizard = 0
        
        # Register handlers for Pop Bumpers
        self.add_mode_event_handler('s_pop_bumper_1_active', self._pop_bumper_hit)
        self.add_mode_event_handler('s_pop_bumper_2_active', self._pop_bumper_hit)
        self.add_mode_event_handler('s_pop_bumper_3_active', self._pop_bumper_hit)
        
        # Register handlers for phase completion
        self.add_mode_event_handler('phase1_wizard_complete', self._phase1_complete)
        self.add_mode_event_handler('s_left_ramp_entry_1_active', self._left_ramp_hit)
        
        # Activate the VUK for Wizard mode
        self.machine.coils.c_mode_vuk.enable()
        
        # Show special intro for wizard mode
        self.machine.events.post('wizard_intro_show')
        
        # Update display to inform player of objectives
        self.machine.events.post('mode_objectives_update', 
                               text="WIZARD MODE: HIT POP BUMPERS!")
        
    def mode_stop(self, **kwargs):
        self.log.info("Wizard mode stopped")
        
        # Disable VUK
        self.machine.coils.c_mode_vuk.disable()
        
        # Reset all modes since wizard mode is complete
        self.machine.events.post('reset_all_modes')
        
    def _pop_bumper_hit(self, **kwargs):
        # Count is handled by the counter
        pass
        
    def _phase1_complete(self, **kwargs):
        self.log.info("Wizard Mode Phase 1 complete - Boiler Room TNT Prep")
        self.player.phase1_complete = True
        
        # Update display to inform player of new objective
        self.machine.events.post('mode_objectives_update', 
                               text="HIT LEFT RAMP TO DETONATE TNT!")
        
        # Special effects for TNT prep
        self.machine.events.post('wizard_tnt_prep')
        
    def _left_ramp_hit(self, **kwargs):
        if self.player.phase1_complete:
            self.log.info("Left ramp hit while phase 1 complete - Completing Wizard mode")
            # Special explosion effects
            self.machine.events.post('wizard_tnt_explosion')
            # Complete the wizard mode
            self.machine.events.post('wizard_phase_2_complete')
