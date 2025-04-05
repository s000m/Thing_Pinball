from mpf.core.mode import Mode
import time

class Service(Mode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_menu = 0
        self.menu_items = ["TEST SWITCHES", "TEST COILS", "TEST LIGHTS", "EXIT SERVICE MODE"]
        self.current_coil = 0
        self.coil_list = []
        self.current_light = 0
        self.light_list = []
        self.menu_active = True
        self.switch_test_active = False
        self.coil_test_active = False
        self.light_test_active = False
        self.start_hold_time = 0
        
    def mode_start(self, **kwargs):
        self.log.info("Service mode started")
        
        # Initialize menu
        self.current_menu = 0
        self.menu_active = True
        
        # Collect all coils and lights for testing
        self.coil_list = list(self.machine.coils.values())
        self.light_list = list(self.machine.lights.values()) if hasattr(self.machine, 'lights') else []
        
        # Register event handlers for menu navigation
        self.add_mode_event_handler('s_left_flipper_button_active', self._left_flipper)
        self.add_mode_event_handler('s_right_flipper_button_active', self._right_flipper)
        self.add_mode_event_handler('s_start_button_active', self._start_pressed)
        self.add_mode_event_handler('s_start_button_inactive', self._start_released)
        
        # Register handlers for all switches to test them
        for switch in self.machine.switches.values():
            self.add_mode_event_handler(f'{switch.name}_active', self._switch_active)
            self.add_mode_event_handler(f'{switch.name}_inactive', self._switch_inactive)
            
        # Disable flippers since we're using them for navigation
        self.machine.flippers.left_flipper.disable()
        self.machine.flippers.right_flipper.disable()
        
        # Show the service menu
        self.machine.events.post('show_service_menu')
        
    def mode_stop(self, **kwargs):
        self.log.info("Service mode stopped")
        # Re-enable flippers
        if self.machine.game and self.machine.game.player:
            self.machine.flippers.left_flipper.enable()
            self.machine.flippers.right_flipper.enable()
            
    def _left_flipper(self, **kwargs):
        if self.menu_active:
            self.current_menu = (self.current_menu - 1) % len(self.menu_items)
            self._update_menu()
        elif self.coil_test_active:
            self.current_coil = (self.current_coil - 1) % len(self.coil_list)
            self._update_coil_display()
        elif self.light_test_active:
            self.current_light = (self.current_light - 1) % len(self.light_list)
            self._update_light_display()
            
    def _right_flipper(self, **kwargs):
        if self.menu_active:
            self.current_menu = (self.current_menu + 1) % len(self.menu_items)
            self._update_menu()
        elif self.coil_test_active:
            self.current_coil = (self.current_coil + 1) % len(self.coil_list)
            self._update_coil_display()
        elif self.light_test_active:
            self.current_light = (self.current_light + 1) % len(self.light_list)
            self._update_light_display()
            
    def _start_pressed(self, **kwargs):
        self.start_hold_time = time.time()
        
        if self.menu_active:
            self._select_menu_item()
        elif self.switch_test_active:
            # Return to menu
            self.switch_test_active = False
            self.menu_active = True
            self.machine.events.post('show_service_menu')
        elif self.coil_test_active:
            # Fire the selected coil
            if self.coil_list:
                self.coil_list[self.current_coil].pulse()
        elif self.light_test_active:
            # Toggle the selected light
            if self.light_list:
                light = self.light_list[self.current_light]
                if light.hw_driver.current_brightness > 0:
                    light.off()
                else:
                    light.on()
                    
    def _start_released(self, **kwargs):
        # Check if this was a long press (hold)
        if time.time() - self.start_hold_time > 1.0:
            if self.coil_test_active or self.light_test_active:
                # Return to menu on long press
                self.coil_test_active = False
                self.light_test_active = False
                self.menu_active = True
                self.machine.events.post('show_service_menu')
                
    def _select_menu_item(self):
        if self.current_menu == 0:  # Test Switches
            self.menu_active = False
            self.switch_test_active = True
            self.machine.events.post('show_switch_test')
        elif self.current_menu == 1:  # Test Coils
            self.menu_active = False
            self.coil_test_active = True
            self.current_coil = 0
            self.machine.events.post('show_coil_test')
            self._update_coil_display()
        elif self.current_menu == 2:  # Test Lights
            self.menu_active = False
            self.light_test_active = True
            self.current_light = 0
            self.machine.events.post('show_light_test')
            self._update_light_display()
        elif self.current_menu == 3:  # Exit Service Mode
            self.machine.events.post('service_mode_stop')
            
    def _update_menu(self):
        # Highlight the current menu item
        for i, item in enumerate(self.menu_items):
            color = "yellow" if i == self.current_menu else "white"
            self.machine.widgets.widget_by_key(f'menu_item_{i}').update({'color': color})
            
    def _switch_active(self, **kwargs):
        if self.switch_test_active:
            # Display the active switch
            switch_name = kwargs.get('switch_name', 'unknown')
            self.machine.widgets.widget_by_key('switch_name').update({'text': f"SWITCH ACTIVE: {switch_name}"})
            
    def _switch_inactive(self, **kwargs):
        if self.switch_test_active:
            # Display the inactive switch
            switch_name = kwargs.get('switch_name', 'unknown')
            self.machine.widgets.widget_by_key('switch_name').update({'text': f"SWITCH RELEASED: {switch_name}"})
            
    def _update_coil_display(self):
        if self.coil_list:
            coil_name = self.coil_list[self.current_coil].name
            self.machine.widgets.widget_by_key('coil_name').update({'text': f"COIL: {coil_name}"})
            
    def _update_light_display(self):
        if self.light_list:
            light_name = self.light_list[self.current_light].name
            self.machine.widgets.widget_by_key('light_name').update({'text': f"LIGHT: {light_name}"})
