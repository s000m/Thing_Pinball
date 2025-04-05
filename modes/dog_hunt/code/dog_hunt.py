from mpf.core.mode import Mode

class DogHunt(Mode):
    def mode_start(self, **kwargs):
        self.log.info("Dog Hunt mode started")
        # Set player variable indicating we're in this mode
        self.player.game_mode_active = True
        self.player.current_game_mode = "dog_hunt"
        
        # Spell "DOG" by activating the bank targets
        self.add_mode_event_handler('dog_bank_targets_complete', self._dog_spelled)
        
        # Activate the VUK
        self.machine.coils.c_mode_vuk.pulse()
        
    def mode_stop(self, **kwargs):
        self.log.info("Dog Hunt mode stopped")
        
        # Disable VUK
        self.machine.coils.c_mode_vuk.disable()
        
    def _dog_spelled(self, **kwargs):
        self.log.info("DOG spelled! Dog Hunt mode phase advancing.")
        # Activate Dog Hunt mode specifics
        
        # The DOG targets are hit, now player must hit spinner to complete the objective
        self.machine.events.post('dog_hunt_phase_1')
        
        # Update display to inform player
        self.machine.events.post('mode_objectives_update', 
                                text="HIT THE SPINNER 100 TIMES!")
