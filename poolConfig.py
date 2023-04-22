import ujson

class Config:
    """Config values for the controller"""
    def __init__(self):
        """At startup each time, read the config file for set temperatures"""
        with open('config.json', 'r') as file:
            base_config = ujson.loads(file.read())
        self.keys = ['min_cycle_time', 'max_water_temp', 'temp_range_for_open', 'temp_range_for_close', 'change_requests_per_minute']
        self.min_cycle_time = base_config['min_cycle_time']
        self.max_water_temp = base_config['max_water_temp']
        self.temp_range_for_open = base_config['temp_range_for_open']
        self.temp_range_for_close = base_config['temp_range_for_close']
        self.change_requests_per_minute = base_config['change_requests_per_minute']
    
    def _write_config(self):
        """When requested, save the changed config values"""
        config = {'min_cycle_time': self.min_cycle_time, 'max_water_temp': self.max_water_temp,
                  'temp_range_for_open': self.temp_range_for_open, 'temp_range_for_close': self.temp_range_for_close,
                  'change_requests_per_minute':self.change_requests_per_minute}
        with open('config.json', 'w') as file:
            file.write(ujson.dumps(config))
    
    def set_max_water_temp(self, max_temp):
        self.max_water_temp = max_temp
        self._write_config()
    
    def set_temp_range_for_open(self, temp_range):
        self.temp_range_for_open = temp_range
        self._write_config()
        
    def set_temp_range_for_close(self, temp_range):
        self.temp_range_for_close = temp_range
        self._write_config()
    
    def set_change_requests_per_minute(self, num):
        self.change_requests_per_minute = num
        self._write_config()
    