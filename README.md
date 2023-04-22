# SolarValveController

Micropython script to control a 24VAC pool solar valve. 
Running on a Raspberry Pi Pico W, with thermister temperature inputs from the pool water intake and roof solar return.
Based on adjustable logic, a relay is used to control the status of the solar valve.

Framework for the API is a lightweight version of flask called microdot. https://microdot.readthedocs.io/en/latest/
