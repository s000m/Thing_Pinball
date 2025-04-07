from mpf.core.mode import Mode

class BallLock(Mode):
    def mode_start(self, **kwargs):
        self.log.info("Ball Lock mode started")
        
        # Set player variables indicating we're in this mode
        self.player.game_mode_active = True
        self.player.current_game_mode = "ball_lock"
        self.player.ball_lock_active = True
    
        # Register event handlers for specific shots
        self.add_mode_event_handler('s_right_orbit_1_active', self._right_orbit_hit)
        
        # Add handler for ball lock event to update player variable
        self.add_mode_event_handler('multiball_lock_ball_lock_locked_ball', self._on_ball_locked)
        
        # Add handler for when lock is full
        self.add_mode_event_handler('multiball_lock_ball_lock_full', self._on_lock_full)
        
        # Pulse the VUK coil at mode start
        self.machine.coils['c_mode_vuk'].pulse()
    
        # Update display
        self.machine.events.post('mode_objectives_update', text="BALL LOCK MODE ACTIVE!")
        
    def mode_stop(self, **kwargs):
        self.log.info("Ball Lock mode stopped")
        
        # Reset player variables
        self.player.ball_lock_active = False
        
        # Disable any hardware that needs to be reset
        self.machine.coils['c_diverter'].disable()
        self.machine.coils['c_up_post'].disable()  # Ensure post is down when mode stops
        
        # Post any needed cleanup events
        self.machine.events.post('ball_lock_mode_ended')
    
    def _right_orbit_hit(self, **kwargs):
        """Handle right orbit hits during ball lock mode."""
        self.log.info("Right Orbit hit - Firing ramp release")
        
        # Post the event that will trigger the coil player in your config
        self.machine.events.post('fire_ramp_release')
        
    def _on_ball_locked(self, **kwargs):
        """Called when a ball is successfully locked."""
        # Get the total locked balls from the multiball lock
        lock_count = self.machine.multiball_locks.ball_lock.locked_balls
        
        self.log.info(f"Ball locked! Current locked balls: {lock_count}")
        
        # Update player-specific counter for UI purposes
        self.player.locked_balls = lock_count
        
        # Update UI with locked ball count
        self.machine.events.post('mode_objectives_update', 
                               text=f"BALL LOCKED! {lock_count}/3")
    
    def _on_lock_full(self, **kwargs):
        """Called when the lock is full (3 balls)."""
        self.log.info("Ball lock full! Enabling up post for 3 seconds")
        
        # Enable the up post coil with hold power to keep it energized
        self.machine.coils['c_up_post'].enable()
        
        # Schedule the disable event after 3 seconds
        self.delay.add(ms=3000, callback=self._disable_up_post, name='disable_up_post')
        
        # Update UI
        self.machine.events.post('mode_objectives_update', 
                               text="LOCK FULL! MULTIBALL READY!")
    
    def _disable_up_post(self):
        """Called after the delay to disable the up post."""
        self.log.info("Disabling up post after delay")
        # Explicitly disable the coil to ensure it's turned off
        self.machine.coils['c_up_post'].disable()
        
        # Post an event that we can use for other game logic if needed
        self.machine.events.post('ball_lock_up_post_disabled')