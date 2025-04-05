from mpf.core.mode import Mode

class Multiball(Mode):
    def mode_start(self, **kwargs):
        self.log.info("Multiball mode started")
        # Set player variable indicating we're in this mode
        self.player.game_mode_active = True
        self.player.current_game_mode = "multiball"
        self.player.jackpot_state = 0
        self.player.right_ramp_valid = False
        
        # Register handlers for the special shots
        self.add_mode_event_handler('s_left_ramp_entry_1_active', self._left_ramp_hit)
        self.add_mode_event_handler('s_right_ramp_entry_1_active', self._right_ramp_hit)
        
        # Monitor ball drains
        self.add_mode_event_handler('ball_drain', self._ball_drained)
        
        # Release the locked balls to start multiball
        self._start_multiball()
        
        # Update display to inform player of objectives
        self.machine.events.post('mode_objectives_update', 
                               text="MULTIBALL! SHOOT LEFT RAMP FOR PULSE UPRAMP!")
        
    def mode_stop(self, **kwargs):
        self.log.info("Multiball mode stopped")
        
    def _start_multiball(self):
        # Start the multiball
        self.machine.multiballs.thing_multiball.start()
        self.log.info("Starting multiball with 4 balls")
        
        # Enable the pulse coil upramp
        self.machine.coils.c_upramp.enable()
        
    def _left_ramp_hit(self, **kwargs):
        # Left ramp advances jackpot state in multiball
        if self.player.jackpot_state == 0:
            self.log.info("Left ramp hit - Activating ball 1")
            self.player.jackpot_state = 1
            self.machine.events.post('ball_1_locked')
            self.machine.events.post('mode_objectives_update', 
                                  text="BALL 1 LOCKED - SHOOT LEFT RAMP AGAIN!")
            
        elif self.player.jackpot_state == 1:
            self.log.info("Left ramp hit - Activating ball 2")
            self.player.jackpot_state = 2
            self.machine.events.post('ball_2_locked')
            self.machine.events.post('mode_objectives_update', 
                                  text="BALL 2 LOCKED - SHOOT LEFT RAMP AGAIN!")
            
        elif self.player.jackpot_state == 2:
            self.log.info("Left ramp hit - Activating ball 3")
            self.player.jackpot_state = 3
            self.machine.events.post('ball_3_locked')
            
            # Enable the jackpot on the right ramp
            self.player.right_ramp_valid = True
            self.machine.events.post('right_ramp_valid')
            self.machine.events.post('mode_objectives_update', 
                                  text="JACKPOT READY! SHOOT RIGHT RAMP!")
            
        elif self.player.jackpot_state == 3 and not self.player.right_ramp_valid:
            # Already at max state but right ramp timeout - re-enable right ramp
            self.player.right_ramp_valid = True
            self.machine.events.post('right_ramp_valid')
            self.machine.events.post('mode_objectives_update', 
                                  text="JACKPOT READY AGAIN! SHOOT RIGHT RAMP!")
            
    def _right_ramp_hit(self, **kwargs):
        # Right ramp collects jackpot when valid
        if self.player.jackpot_state == 3 and self.player.right_ramp_valid:
            self.log.info("Right ramp hit with valid jackpot - Jackpot collected!")
            self.machine.events.post('jackpot_hit')
            
            # Increase jackpot value for next collection
            self.player.jackpot_value += 10000
            
            # Invalidate right ramp temporarily
            self.player.right_ramp_valid = False
            self.machine.events.post('right_ramp_invalid')
            
            # After a short delay, make it valid again
            self.delay.add(callback=self._reactivate_right_ramp, ms=5000)
            
        elif self.player.jackpot_state == 4:
            # Super jackpot hit!
            self.log.info("Right ramp hit for SUPER JACKPOT!")
            self.machine.events.post('super_jackpot_hit')
            
            # Complete the multiball mode after super jackpot
            self.delay.add(callback=self._complete_multiball, ms=3000)
            
    def _reactivate_right_ramp(self):
        if self.player.jackpot_state == 3:
            self.player.right_ramp_valid = True
            self.machine.events.post('right_ramp_valid')
            self.machine.events.post('mode_objectives_update', 
                                  text="JACKPOT READY AGAIN! SHOOT RIGHT RAMP!")
            
    def _ball_drained(self, **kwargs):
        # Post an event when a ball drains
        self.machine.events.post('multiball_drain')
        
        # Check if only one ball remains
        if self.machine.playfield.balls == 1:
            self.log.info("Multiball ended - only one ball remains")
            # Complete the mode if necessary
            self._check_multiball_complete()
            
    def _check_multiball_complete(self):
        # If player achieved all jackpot states, complete successfully
        if self.player.jackpot_state >= 3:
            self.machine.events.post('multiball_complete')
        else:
            self.machine.events.post('multiball_failed')
            
    def _complete_multiball(self):
        self.machine.events.post('multiball_complete')