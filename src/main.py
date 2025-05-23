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
from threading import Thread
import logging
import openvr
from pathlib import Path
from datetime import datetime

from utils import is_vrchat_running, fatal, exit as _exit, spawn_task

EXEDIR = Path(sys.prefix) if getattr(sys, 'frozen', False) else Path(__file__).parent
print(Path(__file__).parent, Path(sys.prefix), EXEDIR)


async def wait_get_oscquery_client():
	service_info = None
	logging.info('Waiting for VRChat to be discovered.')
	while service_info is None:
		browser = OSCQueryBrowser()
		await asyncio.sleep(2)  # Wait for discovery
		service_info = browser.find_service_by_name('VRChat')
	logging.info(f'VRChat discovered! {service_info}')
	client = OSCQueryClient(service_info)
	logging.info('Waiting for VRChat to be ready.')
	while not (avatar_details := await asyncio.to_thread(client.query_node, AVATAR_CHANGE_PARAMETER)):
		sys.stdout.write('.')
		sys.stdout.flush()
		await asyncio.sleep(2)  # Wait for discovery
	logging.info(f'VRChat ready! Avatar: {avatar_details.value}')
	return client


### revelation: holding buttons cancel auf widersen
#!!!


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
		logging.debug(f'on_fire={on}')
		await self.set_fire(on)

	async def on_water(self, on=True):
		logging.debug(f'on_water={on}')
		await self.set_water(on)

	async def on_water_effect(self, on):
		logging.debug(f'on_water_effect={on}')
		self.water = on

	async def on_fire_effect(self, on):
		logging.debug(f'on_fire_effect={on}')
		self.fire = on

	async def set_fire(self, on=True):
		logging.debug(f'set_fire={on}')
		if on and self.water:
			await self.set_water(False)
		self.fire = on
		self.fire_last_changed = datetime.now()
		await self.send_fire(on)

	async def set_water(self, on=True):
		logging.debug(f'set_water={on}')
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
		print(f'send_water {on} at {self.water_last_changed}')

	async def send_fire(self, on=True):
		print('send_fire', on)


def exit(n=0):
	if oscqs:
		asyncio.run(oscqs.stop())
	_exit(n)


logging.basicConfig(
	level=logging.DEBUG,
	format='%(asctime)s %(levelname)s %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S',
	handlers=[logging.StreamHandler(), logging.FileHandler(EXEDIR / 'debug.log', mode='w')],
)
conflocation = EXEDIR / 'config.json'

try:
	with conflocation.open('r') as f:
		conf = json.load(f)
except FileNotFoundError as e:
	raise
except json.JSONDecodeError as e:
	raise

changed = False
vrc: udp_client.SimpleUDPClient | None = None
osc_receiver: osc_server.AsyncIOOSCUDPServer | None = None
qclient: OSCQueryClient | None = None
oscqs: OSCQueryService | None = None

main_loop = asyncio.get_event_loop()  # type: ignore
main_loop.set_debug(True)

OSC_CLIENT_PORT = conf['vrc_osc_port']
OSC_SERVER_IP = conf['vrc_osc_ip']

HTTP_PORT = conf.get('http_port') or 0
OSC_SERVER_PORT = conf.get('server_port') or 0

AVATAR_CHANGE_PARAMETER = '/avatar/change'

if OSC_SERVER_PORT != 9001:
	if OSC_SERVER_PORT <= 0 or not check_if_udp_port_open(OSC_SERVER_PORT):
		OSC_SERVER_PORT = get_open_udp_port()
	if HTTP_PORT <= 0 or not check_if_tcp_port_open(HTTP_PORT):
		HTTP_PORT = OSC_SERVER_PORT if check_if_tcp_port_open(OSC_SERVER_PORT) else get_open_tcp_port()

logging.info(f'Status: OSC_SERVER_PORT={OSC_SERVER_PORT} OSC_CLIENT_PORT={OSC_CLIENT_PORT} HTTP_PORT={HTTP_PORT}')


def reg_openvr():
	global application
	try:
		application = openvr.init(openvr.VRApplication_Utility)
		print(
			EXEDIR / 'app.vrmanifest',
			openvr.VRApplications().addApplicationManifest(str((EXEDIR / 'app.vrmanifest').resolve())),
		)

	except Exception as e:
		fatal(str(e))


async def start_oscq_service():
	# needs to be in thread as it uses asyncio internally???
	global oscqs
	oscqs = OSCQueryService('VR-audience-fire', HTTP_PORT, OSC_SERVER_PORT)
	oscqs.advertise_endpoint(AVATAR_CHANGE_PARAMETER)
	oscqs.advertise_endpoint('/avatar/parameters/fire')
	oscqs.advertise_endpoint('/avatar/parameters/fire_effect')
	oscqs.advertise_endpoint('/avatar/parameters/water')
	oscqs.advertise_endpoint('/avatar/parameters/water_effect')
	logging.info(f'oscqs.httpPort={oscqs.httpPort}')
	await oscqs.start()


def setup_dispatcher(loop: asyncio.BaseEventLoop):
	global disp
	disp = dispatcher.Dispatcher()
	disp.map(AVATAR_CHANGE_PARAMETER, avatar_change)

	def wrap_bool(cb):
		def _wrapper(key, *val):
			logging.info(f'{key} {val}')
			spawn_task(cb(bool(val[0])))

		return _wrapper

	disp.map('/avatar/parameters/fire', wrap_bool(audience_fire.on_fire))
	disp.map('/avatar/parameters/fire_effect', wrap_bool(audience_fire.on_fire_effect))
	disp.map('/avatar/parameters/water', wrap_bool(audience_fire.on_water))
	disp.map('/avatar/parameters/water_effect', wrap_bool(audience_fire.on_water_effect))
	# disp.set_default_handler(asdqwe)


async def init_main():
	global disp, vrc, osc_receiver, osc_server, qclient, audience_fire, transport, protocol, main_loop

	audience_fire = AudienceFire()

	try:
		vrc = udp_client.SimpleUDPClient(OSC_SERVER_IP, OSC_CLIENT_PORT)

		setup_dispatcher(main_loop)

		osc_receiver = osc_server.AsyncIOOSCUDPServer((OSC_SERVER_IP, OSC_SERVER_PORT), disp, main_loop)
		transport, protocol = await osc_receiver.create_serve_endpoint()

		logging.info('Waiting for VRChat to start')
		while not is_vrchat_running():
			await asyncio.sleep(5)
		logging.info('VRChat application detected! Waiting for OSC...')
		qclient = await wait_get_oscquery_client()

		await start_oscq_service()

		try:
			while is_vrchat_running():
				print('.')
				await asyncio.sleep(7)
		except asyncio.exceptions.CancelledError:
			pass
		# https://docs.python.org/3/library/asyncio-task.html#task-cancellation

		logging.info('VRChat closed, exiting.')
		exit()
	except OSError as e:
		if 'debugpy' in sys.modules:
			raise
		else:
			fatal(str(e))
	except zeroconf._exceptions.NonUniqueNameException as e:
		logging.error('NonUniqueNameException, trying again...')
		os.execv(sys.executable, ['python'] + sys.argv)
	except KeyboardInterrupt:
		exit()
	except Exception as e:
		if 'debugpy' in sys.modules:
			raise
		else:
			fatal(str(e))


main_loop.run_until_complete(init_main())
