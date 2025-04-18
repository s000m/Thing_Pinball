from mpf.core.mode import Mode

class Infected(Mode):

    def mode_start(self, **kwargs):
        self.log.info("Infected mode started")
        
        # Set player variable indicating we're in this mode
        self.player.game_mode_active = True
        self.player.current_game_mode = "infected"

        # Reset any counters if needed (they're mostly YAML based)
        self.player.left_ramp_hits = 0
        self.player.newton_hits = 0

        # Register event handlers for showing progress (optional)
        self.add_mode_event_handler('left_ramp_hit', self._left_ramp_progress)
        self.add_mode_event_handler('newton_hit', self._newton_progress)

        # Register completion handlers
        self.add_mode_event_handler('left_ramp_complete', self._check_completion)
        self.add_mode_event_handler('newton_complete', self._check_completion)

        # Enable VUK coil (assuming still needed for theme)
        self.machine.coils.c_mode_vuk.enable()

        # Display start objective
        self.machine.events.post('mode_objectives_update', text="COMPLETE LEFT RAMP & NEWTON HITS!")

    def mode_stop(self, **kwargs):
        self.log.info("Infected mode stopped")

        # Reset player vars (optional)
        self.player.game_mode_active = False
        self.player.current_game_mode = "none"

    def _left_ramp_progress(self, **kwargs):
        """Update UI or log on left ramp hit (optional)."""
        self.log.debug(f"Left Ramp Hits: {self.player.left_ramp_hits}")

    def _newton_progress(self, **kwargs):
        """Update UI or log on newton hit (optional)."""
        self.log.debug(f"Newton Hits: {self.player.newton_hits}")

    def _check_completion(self, **kwargs):
        """Check if both objectives are complete."""
        # Check if both counters are complete
        if (self.player.left_ramp_hits >= 3 and
            self.player.newton_hits >= 3):
            self.log.info("All objectives completed - Ending Infected mode")
            self.machine.events.post('infected_complete')
