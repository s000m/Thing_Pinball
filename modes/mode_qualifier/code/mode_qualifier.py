from mpf.core.mode import Mode


class ModeQualifier(Mode):
    """Mode that manages mode qualification logic."""

    def mode_start(self, **kwargs):
        """Called when mode starts."""
        self.log.info("Mode Qualifier started")
        
        # Register event handlers for mode qualification
        self.add_mode_event_handler('qualify_dog_hunt_mode', self._qualify_dog_hunt_mode)
        self.add_mode_event_handler('clear_qualified_mode', self._clear_qualified_mode)
        
        # Register handler for mode VUK with dog hunt mode qualified
        self.add_mode_event_handler('s_mode_opto_active', self._check_qualified_mode)
        
        # Clear any qualified mode on mode start (just to be safe)
        self._clear_qualified_mode()
        
    def _qualify_dog_hunt_mode(self, **kwargs):
        """Qualify the dog hunt mode."""
        self.log.info("Dog Hunt mode qualified")
        # Set machine variable for dog hunt mode
        self.machine.variables.set_machine_var("qualified_mode", "dog_hunt")
        # Post event for UI and other game elements
        self.machine.events.post("mode_qualification_achieved")
        
    def _clear_qualified_mode(self, **kwargs):
        """Clear any qualified mode."""
        self.log.info("Clearing qualified mode")
        # Reset the machine variable
        self.machine.variables.set_machine_var("qualified_mode", "none")
        
    def _check_qualified_mode(self, **kwargs):
        """Check if a mode is qualified when VUK is hit."""
        qualified_mode = self.machine.variables.get_machine_var("qualified_mode")
        
        if qualified_mode == "dog_hunt":
            self.log.info("Starting Dog Hunt mode due to qualified hit")
            # Start dog hunt mode
            self.machine.events.post("mode_dog_hunt_start")
            # Clear qualification
            self._clear_qualified_mode()