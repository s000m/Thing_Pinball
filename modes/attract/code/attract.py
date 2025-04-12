from mpf.core.mode import Mode

class Attract(Mode):
    def mode_start(self, **kwargs):
        # Register handler for the start button
        self.add_mode_event_handler('s_start_button_active', self._start_button_pressed)
        
    def _start_button_pressed(self, **kwargs):
        # Check if there are enough balls available to play
        if self.machine.ball_controller.num_balls_known < 1:
            self.log.warning("Machine not playable, cannot start game.")
            self.machine.events.post('cannot_start_game_ball_count')
            return
        
        # Request to start game
        self.log.info("Start button pressed. Starting game...")
        self.machine.events.post('request_to_start_game')
