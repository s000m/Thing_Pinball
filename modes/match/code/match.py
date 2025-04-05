from mpf.core.mode import Mode
import random

class Match(Mode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.match_number = None
        self.player_scores = []
        
    def mode_start(self, **kwargs):
        self.log.info("Match mode started")
        
        # Register handler for match setup
        self.add_mode_event_handler('setup_match', self._setup_match)
        
    def _setup_match(self, **kwargs):
        # If there was no game, don't do a match
        if not self.machine.game or not self.machine.game.player_list:
            self.machine.events.post('match_complete')
            return
            
        # Get the last digits of each player's score
        self.player_scores = []
        for player in self.machine.game.player_list:
            # Get last two digits
            last_two_digits = player.score % 100
            self.player_scores.append(last_two_digits)
            
        # Pick a random match number
        self.match_number = random.randint(0, 99)
        
        # Format the number with a leading zero if needed
        match_num_display = f"{self.match_number:02d}"
        
        # Update the match display
        self.machine.widgets.widget_by_key('match_number').update({'text': match_num_display})
        
        # Post match display
        self.machine.events.post('match_display_slide')
        
        # Check if any player gets a match
        match_winners = []
        for i, score_digits in enumerate(self.player_scores):
            if score_digits == self.match_number:
                match_winners.append(i + 1)  # Player numbers are 1-indexed
                
        # After a delay, show match result
        self.delay.add(callback=self._show_match_result,
                      ms=5000,
                      match_winners=match_winners)
                      
    def _show_match_result(self, match_winners):
        if match_winners:
            # Someone matched
            winner_text = "PLAYER "
            if len(match_winners) == 1:
                winner_text += str(match_winners[0])
            else:
                # Multiple winners
                winner_text = "PLAYERS "
                winner_text += ", ".join([str(w) for w in match_winners])
            
            self.machine.events.post('match_winner', winner=winner_text)
            self.machine.events.post('award_match')
        else:
            # No match
            self.machine.events.post('no_match')
            
        # After showing results, end the mode
        self.delay.add(callback=self._end_match, ms=3000)
        
    def _end_match(self):
        self.machine.events.post('match_complete')
