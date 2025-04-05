"""Game mode code for Thing Pinball."""
from mpf.modes.game.code.game import Game as GameBase


class Game(GameBase):
    """Game mode for Thing Pinball."""

    def mode_init(self):
        """Initialize mode."""
        super().mode_init()
        self.log.info("Thing Pinball Game mode initialized")
    
    def mode_start(self, **kwargs):
        """Mode start function."""
        super().mode_start(**kwargs)
        self.log.info("Thing Pinball Game mode started")
        self.add_mode_event_handler('ball_ending', self._calculate_bonus)
    
    def _calculate_bonus(self, **kwargs):
        """Calculate end-of-ball bonus."""
        player = self.machine.game.player
        
        # Basic bonus based on playfield completions
        bonus = 0
        
        # 10k bonus for each completed game mode
        if hasattr(player, 'dog_hunt_complete') and player.dog_hunt_complete:
            bonus += 10000
        if hasattr(player, 'discovery_complete') and player.discovery_complete:
            bonus += 10000
        if hasattr(player, 'infected_complete') and player.infected_complete:
            bonus += 10000
        if hasattr(player, 'blood_test_complete') and player.blood_test_complete:
            bonus += 10000
        if hasattr(player, 'spider_head_complete') and player.spider_head_complete:
            bonus += 10000
        if hasattr(player, 'wizard_complete') and player.wizard_complete:
            bonus += 10000
        if hasattr(player, 'ball_lock_complete') and player.ball_lock_complete:
            bonus += 10000
        if hasattr(player, 'multiball_complete') and player.multiball_complete:
            bonus += 10000
        
        # Set the end bonus for scoring
        player.end_bonus = bonus
        
        self.log.info("End of ball bonus: %s", bonus)
        
        # Show the bonus
        if bonus > 0:
            self.machine.events.post('show_bonus_score', bonus=bonus)