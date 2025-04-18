from mpf.core.mode import Mode

class DogHunt(Mode):

    def mode_start(self, **kwargs):
        self.log.info("Dog Hunt mode started")
        
        # Set player variable indicating we're in this mode
        self.player.game_mode_active = True
        self.player.current_game_mode = "dog_hunt"

        # Reset spinner value
        self.player.spinner_value = 0

        # Add handler for spinner hits
        self.add_mode_event_handler('s_spinner_active', self._on_spinner_hit)

    def mode_stop(self, **kwargs):
        self.log.info("Dog Hunt mode stopped")
        
        # Reset player variables
        self.player.game_mode_active = False
        self.player.current_game_mode = "none"

        # If mode was completed successfully, mark it as complete
        if hasattr(self, '_mode_completed') and self._mode_completed:
            self.player.dog_hunt_complete = 1
            self.machine.variables.set_machine_var('game_mode_dog_hunt_complete', 1)

    def _on_spinner_hit(self, **kwargs):
        """Handler for spinner hits during Dog Hunt mode"""
        self.log.debug("Spinner hit. Current value: %s", self.player.spinner_value)

        # If the player spins enough, complete the mode
        if self.player.spinner_value >= 100:
            self._complete_mode()

    def _complete_mode(self):
        """Mark the mode as successfully completed"""
        self.log.info("Dog Hunt mode objective completed!")
        self._mode_completed = True

        # Post completion event (will trigger scoring and stop the mode)
        self.machine.events.post('dog_hunt_complete')

        # Update display or animations (if needed)
        self.machine.events.post('mode_objectives_update', 
                                  text="DOG HUNT COMPLETE! +50,000")
