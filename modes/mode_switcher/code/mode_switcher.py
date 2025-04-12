from mpf.core.mode import Mode

class ModeSwitcher(Mode):
    """Simple mode that handles mode qualification and switching."""

    def mode_start(self, **kwargs):
        """Called when mode starts."""
        self.log.info("Mode Switcher started")
        self.machine.variables.set_machine_var("qualified_mode", "none")
        
        # Handler for DOG bank completion
        self.add_mode_event_handler('dog_bank_targets_complete', self._dog_targets_complete)
        
        # Handler for VUK switch
        self.add_mode_event_handler('s_mode_opto_active', self._vuk_hit)
    
    def _dog_targets_complete(self, **kwargs):
        """When DOG bank is completed, qualify dog hunt mode if not already completed."""
        # Only qualify if this player hasn't completed the mode yet
        if not self.player.dog_hunt_complete:
            self.log.info("Qualifying Dog Hunt mode")
            self.machine.variables.set_machine_var("qualified_mode", "dog_hunt")
            self.machine.events.post("mode_qualification_achieved")
            self.machine.events.post("qualify_dog_hunt_mode")
    
    def _vuk_hit(self, **kwargs):
        """When VUK is hit, check which mode is qualified and start it."""
        qualified_mode = self.machine.variables.get_machine_var("qualified_mode")
        
        if qualified_mode == "dog_hunt":
            self.log.info("Starting Dog Hunt mode from VUK hit")
            # Clear qualification
            self.machine.variables.set_machine_var("qualified_mode", "none")
            # Start mode
            self.machine.events.post("mode_dog_hunt_start")
