#!/usr/bin/env python3
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher

import logging, sys, os, threading, time
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc.udp_client import SimpleUDPClient
from pprint import pprint
import asyncio
import sys, socket
from contextlib import suppress
# from asynccmd import Cmd


from os import system

system('title VRChat Joy-Con OSC Connector')

import argparse

# client = SimpleUDPClient("10.0.200.202", 54321)
client = SimpleUDPClient('10.0.9.112', 54321)
client._sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

# client = SimpleUDPClient("10.0.9.53", 9000) # can't remember anymore
vrc = SimpleUDPClient('10.0.6.130', 9000)


def clamp(num, min_value, max_value):
	return max(min(num, max_value), min_value)


brr_limit_time = False

brr_limit_time2 = False
Q = 0.15


def setBrrLevel(brrlevel, brr_limit_time_set=20):
	global brr_limit_time
	brrlevel = clamp(brrlevel * Q, 0, 1.0)
	try:
		if brrlevel <= 0:
			client.send_message('/brr', 0)
		client.send_message('/brr', brrlevel)
	except BlockingIOError:
		print('blok')

	if brrlevel <= 0:
		brr_limit_time = False
	else:
		brr_limit_time = time.time() + brr_limit_time_set


def setBrrLevel2(brrlevel, brr_limit_time_set=20):
	global brr_limit_time
	brrlevel = clamp(brrlevel * Q, 0, 1.0)
	try:
		if brrlevel <= 0:
			client.send_message('/brr2', 0)
		client.send_message('/brr2', brrlevel)
	except BlockingIOError:
		print('blok2')

	if brrlevel <= 0:
		brr_limit_time2 = False
	else:
		brr_limit_time2 = time.time() + brr_limit_time_set


def pizza_on(key, *args):
	print('pizza', key, args)


def fire(key, *args):
	print('FIRE!', key, args)
	vrc.send_message('/avatar/parameters/fire_effect', True)
	vrc.send_message('/avatar/parameters/water_effect', False)
	vrc.send_message('/avatar/parameters/MHoodie', False)
	vrc.send_message('/avatar/parameters/shorts', False)


def water(key, *args):
	print('WATER!', key, args)
	vrc.send_message('/avatar/parameters/fire_effect', False)
	vrc.send_message('/avatar/parameters/water_effect', True)


def goobite(key, *args):
	print('goo!', key, args)
	vrc.send_message('/avatar/parameters/goo', True)


def joyconrumble1(key, *args):
	brrlevel = float(args[0] if (type(args[0]) == int or type(args[0]) == float) else args[0][0])
	brrlevel = clamp(brrlevel * 1.5 - 0.1, 0, 1.0)
	# print(key,"|",args,"=>",brrlevel)
	setBrrLevel(brrlevel)


time_pizza_eaten = 0


def pizza_eating(key, *args):
	brrlevel = float(args[0] if (type(args[0]) == int or type(args[0]) == float) else args[0][0])
	brrlevel = clamp(brrlevel * 1.5 - 0.1, 0, 1.0)
	print('PIZZA', key, '|', args, '=>', brrlevel)
	global time_pizza_eaten
	if not time_pizza_eaten:
		print('pizza eaten')
		vrc.send_message('/avatar/parameters/pizza', False)
	time_pizza_eaten = time.time()


async def pizza_think():
	global time_pizza_eaten
	now = time.time()
	if not time_pizza_eaten:
		return
	if now - time_pizza_eaten < 1.5:
		return
	time_pizza_eaten = False
	vrc.send_message('/avatar/parameters/pizza', True)
	print('restore pizza')


async def pizza_worker():
	while True:
		await asyncio.sleep(0.1)
		await pizza_think()


def joyconrumble2(key, *args):
	brrlevel = float(args[0] if (type(args[0]) == int or type(args[0]) == float) else args[0][0])
	vrc.send_message('/avatar/parameters/progress1', brrlevel)
	brrlevel = clamp(brrlevel * 1.5 - 0.1, 0, 1.0)
	# print(key,"|",args,"=>",brrlevel)
	setBrrLevel2(brrlevel)


def eargrab_stretch(key, *args):
	brrlevel = float(args[0] if (type(args[0]) == int or type(args[0]) == float) else args[0][0])
	brrlevel = clamp(brrlevel, 0, 1.0)
	# print(key,"|",args,"=>",brrlevel)
	setBrrLevel(brrlevel, 1)


def tailgrab_stretch(key, *args):
	brrlevel = float(args[0] if (type(args[0]) == int or type(args[0]) == float) else args[0][0])
	brrlevel = clamp(brrlevel / 0.14, 0, 1.0)
	# print(key,"|",args,"=>",brrlevel)
	setBrrLevel(brrlevel, 1)


def eargrab(key, *args):
	brrlevel = float(args[0] if (type(args[0]) == bool) else args[0][0])
	brrlevel = clamp(brrlevel, 0, 1.0)
	# print(key,"|",args,"=>",brrlevel)
	setBrrLevel(brrlevel, 1)


def tailgrab(key, *args):
	brrlevel = float(args[0] if (type(args[0]) == bool) else args[0][0])
	brrlevel = clamp(brrlevel, 0, 1.0)
	# print(key,"|",args,"=>",brrlevel)
	setBrrLevel(brrlevel, 1)


dispatcher = Dispatcher()
dispatcher.map('/brr', joyconrumble1)
dispatcher.map('/brr2', joyconrumble2)
dispatcher.map('/avatar/parameters/joyconrumble1', joyconrumble1)
dispatcher.map('/avatar/parameters/headpats', joyconrumble1)
dispatcher.map('/avatar/parameters/fire', fire)
dispatcher.map('/avatar/parameters/pizza_eating', pizza_eating)
dispatcher.map('/avatar/parameters/water', water)
dispatcher.map('/avatar/parameters/goobite', goobite)
dispatcher.map('/avatar/parameters/attacked', fire)


def musehr(key, *args):
	hr = float(args[0] if (type(args[0]) == int or type(args[0]) == float) else args[0][0])
	hrremapped = -1.0 + (hr / 255.0) * 2.0
	# print("hr",hr,"->",hrremapped)
	vrc.send_message('/avatar/parameters/HeartRateFloat', hrremapped)


dispatcher.map('/Biometrics/HeartBeatsPerMinute', musehr)

BARSIZE = 20


def HueShift(key, *args):
	hue01 = float(args[0] if (type(args[0]) == int or type(args[0]) == float) else args[0][0])
	# print("hue01     ","="*int(hue01*BARSIZE)+"-"*int(BARSIZE-hue01*BARSIZE))


#       vrc.send_message("/avatar/parameters/progress1", hue01)


def FocusAvgPos(key, *args):
	focuslevel = float(args[0] if (type(args[0]) == int or type(args[0]) == float) else args[0][0])
	# print("focuslevel","="*int(focuslevel*BARSIZE)+"-"*int(BARSIZE-focuslevel*BARSIZE))
	vrc.send_message('/avatar/parameters/progress1', focuslevel)


# dispatcher.map("/Addons/HueShift",HueShift)
# dispatcher.map("/NeuroFB/FocusAvgPos",FocusAvgPos)
dispatcher.map('/NeuroFB/RelaxAvgPos', FocusAvgPos)

# dispatcher.map("/avatar/parameters/joyconrumble2", joyconrumble1)

dispatcher.map('/avatar/parameters/LeftEar_Stretch', eargrab_stretch)
dispatcher.map('/avatar/parameters/RightEar_Stretch', eargrab_stretch)
dispatcher.map('/avatar/parameters/Tail_Stretch', tailgrab_stretch)

dispatcher.map('/avatar/parameters/LeftEar_IsGrabbed', eargrab)
dispatcher.map('/avatar/parameters/RightEar_IsGrabbed', eargrab)
dispatcher.map('/avatar/parameters/Tail_IsGrabbed', tailgrab)

dispatcher.map('/avatar/parameters/pizza', pizza_on)

# dispatcher.set_default_handler(print)
ip = '0.0.0.0'
port = 9009


async def loop():
	global brr_limit_time, brr_limit_time2
	terminal_title = 'VR Microcontroller OSC Haptics v0.2 ESP32-S2 Stereo Edition'
	print(f'\33]0;{terminal_title}\a', end='', flush=True)
	print(terminal_title)

	await asyncio.sleep(1)
	client.send_message('/brr', 1.0)
	client.send_message('/brr2', 0.0)
	await asyncio.sleep(0.5)
	client.send_message('/brr', 0.0)
	client.send_message('/brr2', 1.0)
	await asyncio.sleep(0.5)
	client.send_message('/brr', 0.0)
	client.send_message('/brr2', 0.0)
	while True:
		await asyncio.sleep(0.1)
		if brr_limit_time and time.time() > brr_limit_time:
			brr_limit_time = None
			try:
				client.send_message('/brr', 0.0)
			except BlockingIOError:
				print('BLOK')
			print('Setting brr to 0')

		if brr_limit_time2 and time.time() > brr_limit_time2:
			brr_limit_time2 = None
			try:
				client.send_message('/brr2', 0.0)
			except BlockingIOError:
				print('BLOK')
			print('Setting brr2 to 0')


async def init_main():
	server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
	transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving
	asyncio.create_task(pizza_worker())
	await loop()  # Enter main loop of program

	transport.close()  # Clean up serve endpoint


asyncio.run(init_main())
