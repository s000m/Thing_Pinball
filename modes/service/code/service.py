from mpf.core.mode import Mode

class ServiceMode(Mode):
    def on_load(self):
        self.info_log("Service Mode Scriptlet loaded")
        self.machine.events.add_handler('service_mode_entered', self._service_mode_entered)
        
        # Register a keyboard key to enter service mode (F2)
        self.machine.add_handler("key_f2", self._enter_service_mode)
        
    def _enter_service_mode(self, **kwargs):
        self.info_log("Service mode triggered by keyboard")
        if not self.machine.modes.service.active:
            self.machine.events.post('service_mode_start')
            
    def _service_mode_entered(self, **kwargs):
        self.info_log("Service mode has been entered")
        # Any additional setup that should happen when service mode starts
