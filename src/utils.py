import os
import sys
from psutil import process_iter
from threading import Thread, Timer

import ctypes
import traceback
import logging


class RepeatedTimer(object):
	def __init__(self, interval: float, function, *args, **kwargs):
		self._timer: Timer = None
		self.interval = interval
		self.function = function
		self.args = args
		self.kwargs = kwargs
		self.is_running: bool = False
		self.start()

	def _run(self):
		self.is_running = False
		self.start()
		self.function(*self.args, **self.kwargs)

	def start(self):
		if not self.is_running:
			self._timer = Timer(self.interval, self._run)
			self._timer.start()
			self.is_running = True

	def stop(self):
		self._timer.cancel()
		self.is_running = False


def is_vrchat_running() -> bool:
	"""Checks if VRChat is running."""
	_proc_name = 'VRChat.exe' if os.name == 'nt' else 'VRChat'
	return _proc_name in (p.name() for p in process_iter())


def fatal(msg):
	if 'debugpy' in sys.modules:
		raise Exception(str(msg))

	if os.name == 'nt':
		ctypes.windll.user32.MessageBoxW(0, traceback.format_exc(), 'vr_audience_fire - ERROR', 0)
	else:
		print(msg)
	logging.error(traceback.format_exc())
	exit()


from pydantic import BaseModel, ConfigDict, ValidationError


class Event(BaseModel):
	model_config = ConfigDict(strict=True)

	where: tuple[int, int]


json_data = '{"when": "1987-01-28", "where": [51, 1,-1]}'
print(Event.model_validate_json(json_data))
