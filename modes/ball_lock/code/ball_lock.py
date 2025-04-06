from mpf.core.mode import Mode

class BallLock(Mode):
    def mode_start(self, **kwargs):
        self.log.info("Ball Lock mode started")
        # Set player variable indicating we're in this mode
        self.player.game_mode_active = True
        self.player.current_game_mode = "ball_lock"
        self.player.ball_lock_active = False
        self.player.left_ramp_lock_hits = 0
        
        # Register handlers for Left Ramp
        self.add_mode_event_handler('s_left_ramp_entry_1_active', self._left_ramp_hit)
        
        # Register handlers for the Right Ramp (when enabled)
        self.add_mode_event_handler('s_right_ramp_entry_1_active', self._right_ramp_hit)
        
        # Register for ball capture
        self.add_mode_event_handler('balldevice_bd_ball_lock_ball_enter', self._ball_locked)
        
        # Register for right orbit
        self.add_mode_event_handler('s_right_orbit_1_active', self._right_orbit_hit)
        
        # Pulse the VUK instead of enabling it
        self.machine.coils.c_mode_vuk.pulse()
        
        # Update display to inform player of objectives
        self.machine.events.post('mode_objectives_update', 
                               text="BALL LOCK MODE ACTIVE!")
        
    def mode_stop(self, **kwargs):
        self.log.info("Ball Lock mode stopped")
        
        # Disable orbit pulse and diverter
        self.player.ball_lock_active = False
        self.machine.coils.c_diverter.disable()
        
    def _left_ramp_hit(self, **kwargs):
        # Left ramp hits are handled by the counter
        pass
        
    def _enable_ball_lock(self, **kwargs):
        self.log.info("Ball Lock enabled - Right Ramp will now lock balls")
        self.player.ball_lock_active = True
        
        # Activate diverter to route balls to lock
        self.machine.coils.c_diverter.enable()
        
        # Update display to inform player
        self.machine.events.post('mode_objectives_update', 
                               text="BALL LOCK ENABLED! SHOOT RIGHT RAMP!")
        
    def _right_ramp_hit(self, **kwargs):
        if self.player.ball_lock_active:
            self.log.info("Right Ramp hit with Ball Lock active")
            # Ball diverted to ball lock - Will trigger ball device entered event
            # Pulse the Up Ramp coil to help the ball
            self.machine.coils.c_upramp.pulse()
    
    def _right_orbit_hit(self, **kwargs):
        self.log.info("Right Orbit hit - Firing ramp release")
        # Post the event that will trigger the coil player
        self.machine.events.post('fire_ramp_release')
            
    def _ball_locked(self, **kwargs):
        if self.player.ball_lock_active:
            self.log.info("Ball locked in ball lock device")
            # Increment locked balls
            self.player.locked_balls += 1
            self.machine.events.post('ball_locked')
        
            # Auto-launch a new ball
            self.machine.playfield.add_ball()
        
            try:
                # Get the actual count of balls physically in the lock
                lock_device = self.machine.ball_devices['bd_ball_lock']
                physical_balls = lock_device.balls
                
                self.log.info(f"Physical balls in lock: {physical_balls}")
                
                # Only post ball_lock_complete when exactly 3 balls are locked
                if physical_balls == 3:
                    self.log.info("All 3 balls locked - Ball Lock mode complete")
                    self.machine.events.post('ball_lock_complete')
                else:
                    # Update display with locked balls count
                    self.machine.events.post('mode_objectives_update', 
                                        text=f"BALL LOCKED! {self.player.locked_balls}/3")
            except Exception as e:
                self.log.error(f"Error checking physical balls: {e}")
                # Show current progress based on player variable
                self.machine.events.post('mode_objectives_update', 
                                    text=f"BALL LOCKED! {self.player.locked_balls}/3")