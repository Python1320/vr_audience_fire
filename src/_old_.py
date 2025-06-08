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

# client = SimpleUDPClient("10.0.9.53", 9000) # can't remember anymore
vrc = SimpleUDPClient('10.0.6.130', 9000)


def clamp(num, min_value, max_value):
	return max(min(num, max_value), min_value)


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


dispatcher = Dispatcher()
dispatcher.map('/avatar/parameters/fire', fire)
dispatcher.map('/avatar/parameters/water', water)


# dispatcher.set_default_handler(print)
ip = '0.0.0.0'
port = 9009


async def loop():
	global brr_limit_time, brr_limit_time2
	terminal_title = 'vr_audience_fire v0.1'
	print(f'\33]0;{terminal_title}\a', end='', flush=True)
	print(terminal_title)

	while True:
		await asyncio.sleep(0.1)


async def init_main():
	server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
	transport, protocol = await server.create_serve_endpoint()
	asyncio.create_task(pizza_worker())
	await loop()
	transport.close()


asyncio.run(init_main())
