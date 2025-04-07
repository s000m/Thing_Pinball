from mpf.core.mode import Mode

class BallLock(Mode):
    def mode_start(self, **kwargs):
        self.log.info("Ball Lock mode started")
        # Set player variables indicating we're in this mode
        self.player.game_mode_active = True
        self.player.current_game_mode = "ball_lock"
        self.player.ball_lock_active = True
    
        # Reset locked balls count
        self.player.locked_balls = 0
    
        # Configure the ball lock device to hold balls
        self.machine.ball_devices['bd_ball_lock'].config['eject_on_ball_request'] = False
        
        # To prevent multiple ejects being queued when we don't want them
        self.ball_added_after_lock = False
    
        # Register handlers
        self.add_mode_event_handler('s_right_ramp_entry_1_active', self._right_ramp_hit)
        self.add_mode_event_handler('balldevice_bd_ball_lock_ball_enter', self._ball_locked)
        self.add_mode_event_handler('s_right_orbit_1_active', self._right_orbit_hit)
    
        # Add a more consistent eject prevention with higher priority
        self.add_mode_event_handler('balldevice_bd_ball_lock_ball_eject_attempt', self._prevent_eject, priority=1500)
        
        # Explicitly handle ball drain during ball lock mode
        self.add_mode_event_handler('ball_drain', self._handle_drain)
    
        # Pulse the VUK
        self.machine.coils['c_mode_vuk'].pulse()
    
        # Update display
        self.machine.events.post('mode_objectives_update', text="BALL LOCK MODE ACTIVE!")
        
    def mode_stop(self, **kwargs):
        self.log.info("Ball Lock mode stopped")
        
        # Disable orbit pulse and diverter
        self.player.ball_lock_active = False
        self.machine.coils['c_diverter'].disable()
    
    def _prevent_eject(self, **kwargs):
        # Only block ejections during active collection phase
        if self.player.ball_lock_active and kwargs.get('source') and kwargs['source'].name == 'bd_ball_lock':
            self.log.info("BLOCKING BALL EJECT ATTEMPT - Ball lock mode active")
            self.machine.events.post('ball_lock_eject_blocked')
            return False
        return True  # Allow ejection for other devices
    
    def _handle_drain(self, device, balls, **kwargs):
        self.log.info(f"Ball drained during ball lock mode. From device: {device.name}, Balls: {balls}")
        
        # If a ball drains during ball lock mode but we've already locked a ball
        # and added a replacement, we don't need to add another
        if self.ball_added_after_lock:
            self.log.info("Already added a replacement ball after lock - not adding another")
            return
        
        # Reset this flag for next time
        self.ball_added_after_lock = False
    
    def _right_ramp_hit(self, **kwargs):
        if self.player.ball_lock_active:
            self.log.info("Right Ramp hit with Ball Lock active")
        
            try:
                lock_device = self.machine.ball_devices['bd_ball_lock']
                
                # More robust ball locking check
                if lock_device.balls < 3:
                    self.log.info(f"Requesting ball to lock. Current physical balls: {lock_device.balls}")
                    
                    # Fix: Just call request_ball() without the source parameter
                    lock_device.request_ball()
                    
                    # Post event to track ball lock attempts
                    self.machine.events.post('ball_lock_requested')
                else:
                    self.log.warning("Ball lock is already full. Cannot lock more balls.")
                    self.machine.events.post('ball_lock_full')
            except Exception as e:
                self.log.error(f"Error requesting ball to lock: {e}")
                self.machine.events.post('ball_lock_request_error', error=str(e))
     
    def _right_orbit_hit(self, **kwargs):
        self.log.info("Right Orbit hit - Firing ramp release")
        # Post the event that will trigger the coil player
        self.machine.events.post('fire_ramp_release')

    def _ball_locked(self, **kwargs):
        if self.player.ball_lock_active:
            self.log.info("Ball locked in ball lock device")
            
            # Prevent more than one lock per ball
            if self.ball_added_after_lock:
                self.log.info("Already handled a lock this ball - ignoring additional lock events")
                return True
                
            # Increment locked balls
            self.player.locked_balls += 1
            self.machine.events.post('ball_locked')
        
            try:
                lock_device = self.machine.ball_devices['bd_ball_lock']
                
                # CRITICAL LINE: Tell MPF this ball is expected to be in the device
                lock_device.available_balls = 0
                # Override the number of balls it thinks should be in it
                lock_device._state_handlers['idle'].balls = lock_device.balls
                
                physical_balls = lock_device.balls
                
                self.log.info(f"Physical balls in lock: {physical_balls}")
                
                # Update display with locked balls count
                self.machine.events.post('mode_objectives_update', 
                                    text=f"BALL LOCKED! {self.player.locked_balls}/3")
                                    
                # Mark that we've already added a ball after this lock
                self.ball_added_after_lock = True
                
                # Only check for completion after locking
                if physical_balls == 3:
                    self.log.info("All 3 balls locked - Ball Lock mode complete")
                    self.player.ball_lock_active = False
                    self.machine.events.post('ball_lock_complete')
                    self.machine.events.post('mode_ball_lock_complete')
                    return True
                
                # Add a delay before launching a replacement ball
                self.machine.clock.schedule_once(self._add_replacement_ball, 0.5)
                
            except Exception as e:
                self.log.error(f"Error handling ball lock: {e}")
                # Fallback progress display
                self.machine.events.post('mode_objectives_update', 
                                    text=f"BALL LOCKED! {self.player.locked_balls}/3")
            
            # Return True to interrupt the auto-launch chain
            return True
        return False
        
    def _add_replacement_ball(self, dt):
        """Add a replacement ball after a delay."""
        self.log.info("Adding replacement ball from trough to shooter lane")
        # The critical part - add a new ball from trough to shooter lane
        self.machine.ball_devices['bd_trough'].eject(target=self.machine.ball_devices['bd_shooter_lane'])