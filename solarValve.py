from machine import Pin

class SolarValve:
    """Controller for Solar Valve"""
    def __init__(self, config):
        self.position = Pin(0, Pin.OUT)
        self.delay = 0
        self.config = config
        self.last_valve_change = config.min_cycle_time # init @ min cycle time
        self.temp_range = config.temp_range_for_open # init at the closed setting (high)
        self.change_requests = 0 # number of valve change requests must be x per minute before valve changes - gets reset in main every 60 sec
    
    def set_valve(self, sensors, config):
        """This is run every second to update the valve setting"""
        
        # First guard clause is for if a valve change delay was initiated manually or we are within the cycle limit set by config
        if self.delay > 0 or self.last_valve_change < config.min_cycle_time:
            return
        
        # Second guard clause checks for if we are at max water temp and if so - ensures valve is closed
        if sensors.water_temp >= config.max_water_temp:
            self._close_valve()
            return
        
        # If the roof temp is above the current registered warm value, make sure it get opened, otherwise closed
        if sensors.roof_temp > sensors.water_temp + self.temp_range:
            self._open_valve()
        else:
            self._close_valve()
                
    def _open_valve(self, time=None):
        """Set valve to open if it is closed. Does not account for cycle time, max temp, or delays (but will reset all)"""
        if self.position.value() == 0:
            if self.change_requests >= self.config.change_requests_per_minute:
                self.position(1)
                self.last_valve_change = 0
                self.temp_range = self.config.temp_range_for_close
                if time:
                    self.delay = time
                return True
            else:
                self.change_requests += 1
                return False
        else:
            return False
    
    def _close_valve(self, time=None):
        """Set valve to closed if it is open. Does not account for cycle time, max temp, or delays (but will reset all)"""
        if self.position.value() == 1:
            if self.change_requests >= self.config.change_requests_per_minute:
                self.position(0)
                self.last_valve_change = 0
                self.temp_range = self.config.temp_range_for_open
                if time:
                    self.delay = time
                return True
            else:
                self.change_requests += 1
                return False
        else:
            return False
    
    def manual_open(self, delay=None):
        """Open valve manually and set all constraints. Return False if already open"""
        if self.position.value() == 1:
            return False
        
        self.position(1)
        self.last_valve_change = 0
        self.temp_range = self.config.temp_range_for_close
        if delay:
            self.delay = delay
        return True
    
    def manual_close(self, delay=None):
        """Close valve manually and set all constraints. Return False if already closed"""
        if self.position.value() == 0:
            return False
        
        self.position(0)
        self.last_valve_change = 0
        self.temp_range = self.config.temp_range_for_open
        if delay:
            self.delay = delay
        return True
