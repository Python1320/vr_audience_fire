import asyncio
import json
import os
import sys
import time
import traceback
import ctypes
from typing import Any, List
import zeroconf
from pythonosc import dispatcher, osc_server, udp_client
from tinyoscquery.queryservice import OSCQueryService
from tinyoscquery.utility import (
	get_open_tcp_port,
	get_open_udp_port,
	check_if_tcp_port_open,
	check_if_udp_port_open,
)
from tinyoscquery.query import OSCQueryBrowser, OSCQueryClient
from threading import Thread, Timer
import logging
import openvr
from datetime import datetime

from utils import RepeatedTimer, is_vrchat_running, fatal


def get_absolute_path(relative_path, script_path=__file__) -> str:
	"""Gets absolute path from relative path"""
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(script_path)))
	return os.path.join(base_path, relative_path)


def wait_get_oscquery_client():
	service_info = None
	logging.info('Waiting for VRChat to be discovered.')
	while service_info is None:
		browser = OSCQueryBrowser()
		time.sleep(2)  # Wait for discovery
		service_info = browser.find_service_by_name('VRChat')
	logging.info('VRChat discovered!')
	client = OSCQueryClient(service_info)
	logging.info('Waiting for VRChat to be ready.')
	while client.query_node(AVATAR_CHANGE_PARAMETER) is None:
		time.sleep(2)
	logging.info('VRChat ready!')
	return client


def set_profile(addr, value):
	logging.info(f'Setting profile to {addr} {value}')
	time.sleep(1)
	avatar_change(None, None)


def set_gains():
	global changed

	if not changed:
		return

	changed = False

### revelation: holding buttons cancel auf widersen
!!!

def fire_receiver(addr, value):
	logging.info(f'Fire: {addr} {value}...')


def asdqwe(address: str, *args: List[Any]) -> None:
	print(address, args)


def avatar_change(addr, value):
	logging.info(f'Avatar changed/reset {addr} {value}...')

	# osc_sender.send_message(f"{PARAMETER_PREFIX_IN}gain_{strip}", get_float_from_voicemeeter_gain(vmr.inputs[strip].gain))


class AudienceFire:
	def __init__(self):
		self.fire = False
		self.water = False
		self.water_last_changed = None
		self.fire_last_changed = None
		self._water_task = None

	async def on_fire(self, on=True):
		await self.set_fire(on)

	async def on_water(self, on=True):
		await self.set_water(on)

	async def on_water_effect(self, on):
		self.water = on

	async def on_fire_effect(self, on):
		self.fire = on

	async def set_fire(self, on=True):
		if on and self.water:
			await self.set_water(False)
		self.fire = on
		self.fire_last_changed = datetime.now() 
		await self.send_fire(on)

	async def set_water(self, on=True):
		if on and self.fire:
			await self.set_fire(False)
		self.water = on
		self.water_last_changed = datetime.now()
		await self.send_water(on)

		if on:
			if self._water_task:
				self._water_task.cancel()
			self._water_task = asyncio.create_task(self._auto_stop_water())

	async def _auto_stop_water(self):
		try:
			await asyncio.sleep(5)
			await self.set_water(False)
		except asyncio.CancelledError:
			pass

	async def send_water(self, on=True):
		print(f"send_water {on} at {self.water_last_changed}")

	async def send_fire(self, on=True):
		print("send_fire", on)

def exit():
	logging.info('Exiting...')
	if update_timer:
		update_timer.stop()
	if oscqs:
		oscqs.stop()
	sys.exit(0)


logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(levelname)s - %(message)s',
	datefmt='%d-%b-%y %H:%M:%S',
	handlers=[logging.StreamHandler()],
)

conf = json.load(open(get_absolute_path('config.json')))


changed = False
vrc: udp_client.SimpleUDPClient | None = None
osc_receiver: osc_server.AsyncIOOSCUDPServer | None = None
server_thread: Thread | None = None
qclient: OSCQueryClient | None = None
oscqs: OSCQueryService | None = None
update_timer: RepeatedTimer | None = None

OSC_CLIENT_PORT = conf['port']
OSC_SERVER_PORT = conf['server_port']
OSC_SERVER_IP = conf['ip']
HTTP_PORT = conf['http_port']
AVATAR_CHANGE_PARAMETER = '/avatar/change'

if OSC_SERVER_PORT != 9001:
	logging.info(
		f'OSC Server port ({"finding" if OSC_SERVER_PORT == 0 else OSC_SERVER_PORT}) is not default, testing port availability and advertising OSCQuery endpoints'
	)
	if OSC_SERVER_PORT <= 0 or not check_if_udp_port_open(OSC_SERVER_PORT):
		OSC_SERVER_PORT = get_open_udp_port()
	if HTTP_PORT <= 0 or not check_if_tcp_port_open(HTTP_PORT):
		HTTP_PORT = OSC_SERVER_PORT if check_if_tcp_port_open(OSC_SERVER_PORT) else get_open_tcp_port()
else:
	logging.info('OSC Server port is default.')

try:
	application = openvr.init(openvr.VRApplication_Utility)
	openvr.VRApplications().addApplicationManifest(get_absolute_path('app.vrmanifest'))

except Exception as e:
	fatal(str(e))

async def init_main():
	global disp,vrc,osc_receiver,osc_server,qclient,audience_fire

	audience_fire = AudienceFire()

	try:
		vrc = udp_client.SimpleUDPClient(OSC_SERVER_IP, OSC_CLIENT_PORT)

		disp = dispatcher.Dispatcher()
		disp.map(AVATAR_CHANGE_PARAMETER, avatar_change)
		disp.map('/avatar/parameters/fire', audience_fire.on_fire)
		disp.map('/avatar/parameters/fire_effect', audience_fire.on_fire_effect)
		disp.map('/avatar/parameters/water', audience_fire.on_water)
		disp.map('/avatar/parameters/water_effect', audience_fire.on_water_effect)
		# disp.set_default_handler(asdqwe)
		loop: asyncio.BaseEventLoop = asyncio.get_event_loop() # type: ignore
		
		osc_receiver = osc_server.AsyncIOOSCUDPServer((OSC_SERVER_IP, OSC_SERVER_PORT), disp, loop)
		
		logging.info('Waiting for VRChat to start.')
		while not is_vrchat_running():
			time.sleep(5)
		logging.info('VRChat started!')
		qclient = wait_get_oscquery_client()
		oscqs = OSCQueryService('vr_audience_fire', HTTP_PORT, OSC_SERVER_PORT)
		oscqs.advertise_endpoint(AVATAR_CHANGE_PARAMETER)
		oscqs.advertise_endpoint('/avatar/parameters/fire')
		oscqs.advertise_endpoint('/avatar/parameters/fire_effect')
		oscqs.advertise_endpoint('/avatar/parameters/water')
		oscqs.advertise_endpoint('/avatar/parameters/water_effect')

		avatar_change(None, None)

		update_timer = RepeatedTimer(0.3, set_gains)
		update_timer.start()

		while is_vrchat_running():
			await asyncio.sleep(5)
		#https://docs.python.org/3/library/asyncio-task.html#task-cancellation

		logging.info('VRChat closed, exiting.')
		exit()
	except OSError as e:
		fatal(str(e))
	except zeroconf._exceptions.NonUniqueNameException as e:
		logging.error('NonUniqueNameException, trying again...')
		os.execv(sys.executable, ['python'] + sys.argv)
	except KeyboardInterrupt:
		exit()
	except Exception as e:
		fatal(str(e))


asyncio.run(init_main())
