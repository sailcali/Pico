from microdot_asyncio import Microdot
import network
import time
import uasyncio
from tempSensors import Sensors
from solarValve import SolarValve
from poolConfig import Config

sensors = Sensors()
app = Microdot()
config = Config()
valve = SolarValve(config)

def setup_wifi():
    ssid = 'Home'
    password = 'duke1724'
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )

def standard_response():
    return {"water_temp": sensors.water_temp, "roof_temp": sensors.roof_temp,
            "valve": valve.position.value(), 'delay': valve.delay,
            "last_change": valve.last_valve_change, "set_temp": config.max_water_temp,
            "temp_range": valve.temp_range, "change_requests_per_minute": config.change_requests_per_minute}

@app.route('/')
def status(request):
    response = standard_response()
    return response, 200, {'Content-Type': 'application/json'}

@app.route('/valve', methods=['POST'])
def status(request):
    verify = False
    try:
        delay = int(request.args['delay'])
    except KeyError:
        delay = None
    if request.args['valve'] == "1":
        verify = valve.manual_open(delay)
    elif request.args['valve'] == "0":
        verify = valve.manual_close(delay)
    response = standard_response()
    if verify:
        return response, 200, {'Content-Type': 'application/json'}
    else:
        return {"Error": f"Valve already set to {request.args['valve']}"}, 400, {'Content-Type': 'application/json'}

@app.route('/config', methods=['POST'])
def change_config(request):
    try:
        key = request.args['key']
        value = int(request.args['value'])
        if key not in config.keys:
            return {"Error": "Key is not valid", "keys": config.keys}, 400, {'Content-Type': 'application/json'}
    except KeyError:
        return {"Error": "Please include 'key' and 'value' arguments"}, 400, {'Content-Type': 'application/json'}
    if key == 'max_water_temp':
        config.set_max_water_temp(value)
    elif key == 'temp_range_for_open':
        config.set_temp_range_for_open(value)
    elif key == 'temp_range_for_close':
        config.set_temp_range_for_close(value)
    elif key == 'change_requests_per_minute':
        config.set_change_requests_per_minute(value)
    return {}, 201, {'Content-Type': 'application/json'}

@app.route('/temp', methods=['POST'])
def change_set_temp(request):
    try:
        temp = int(request.args['setting'])
    except KeyError:
        return {"Error": "Please include 'setting' argument"}, 400, {'Content-Type': 'application/json'}
    config.set_max_water_temp(temp)
    
    response = standard_response()
    return response, 200, {'Content-Type': 'application/json'}

@app.route('/shutdown')
def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'

async def maintainer():
    change_request_tracker = 0
    while True:
        # Refresh the current temperatures
        sensors.refresh_temps()
        # Go through algorithm to check for valve change
        valve.set_valve(sensors, config)
        # If the user instituted a delay, reduce that here by a second
        if valve.delay > 0:
            valve.delay -= 1
        # Wait time between cycles is 1 second
        await uasyncio.sleep_ms(1000)
        # Tracking the last valve change value
        valve.last_valve_change += 1
        change_request_tracker += 1
        if change_request_tracker == 60:
            valve.change_requests = 0
            change_request_tracker = 0

if __name__ == "__main__":
    # Get wifi up connected
    setup_wifi()
    
    # Start the function that will continuously run to maintain the solar valve
    uasyncio.create_task(maintainer())
    
    # Flask runs continuously on port 5000
    app.run()
