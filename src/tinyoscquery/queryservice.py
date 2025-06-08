import asyncio
from zeroconf import IPVersion, InterfaceChoice, ServiceInfo, Zeroconf
from aiohttp import web
from .shared.node import OSCQueryNode, OSCHostInfo, OSCAccess
import json, threading


class OSCQueryService(object):
	"""
	A class providing an OSCQuery service. Automatically sets up a oscjson http server and advertises the oscjson server and osc server on zeroconf.

	Attributes
	----------
	serverName : str
	    Name of your OSC Service
	httpPort : int
	    Desired TCP port number for the oscjson HTTP server
	oscPort : int
	    Desired UDP port number for the osc server
	"""

	def __init__(self, serverName, httpPort, oscPort, oscIp='127.0.0.1') -> None:
		self.serverName = serverName
		self.httpPort = httpPort
		self.oscPort = oscPort
		self.oscIp = oscIp

		self.root_node = OSCQueryNode('/', description='root node')
		self.host_info = OSCHostInfo(
			serverName,
			{'ACCESS': True, 'CLIPMODE': False, 'RANGE': True, 'TYPE': True, 'VALUE': True},
			self.oscIp,
			self.oscPort,
			'UDP',
		)

	async def start(self):
		self._zeroconf = Zeroconf(ip_version=IPVersion.V4Only, interfaces=['127.0.0.1'])
		await self._startOSCQueryService()
		await self._advertiseOSCService()  # TODO: seems uncessary and to duplicate VRC messages!
		handler = OSCQueryHTTPServer_handler(self.root_node, self.host_info)
		runner = web.ServerRunner(web.Server(handler))
		await runner.setup()
		site = web.TCPSite(runner, '127.0.0.1', self.httpPort)  # TODO: empty ip?
		await site.start()

	async def stop(self):
		for node in self.root_node.contents:
			self.root_node.remove_child_node(node)
		await self._zeroconf.async_unregister_all_services()

	def add_node(self, node):
		self.root_node.add_child_node(node)

	def advertise_endpoint(self, address, value=None, access=OSCAccess.READWRITE_VALUE):
		new_node = OSCQueryNode(full_path=address, access=access)
		if value is not None:
			if not isinstance(value, list):
				new_node.value = [value]
				new_node.type_ = [type(value)]
			else:
				new_node.value = value
				new_node.type_ = [type(v) for v in value]
		self.add_node(new_node)

	async def _startOSCQueryService(self):
		oscqsDesc = {'txtvers': 1}
		oscqsInfo = ServiceInfo(
			'_oscjson._tcp.local.',
			'%s._oscjson._tcp.local.' % self.serverName,
			self.httpPort,
			0,
			0,
			oscqsDesc,
			None,  # hm
			addresses=['127.0.0.1'],
		)
		await self._zeroconf.async_register_service(oscqsInfo)

	async def _advertiseOSCService(self):
		oscDesc = {'txtvers': 1}
		oscInfo = ServiceInfo(
			'_osc._udp.local.',
			'%s._osc._udp.local.' % self.serverName,
			self.oscPort,
			0,
			0,
			oscDesc,
			'%s.osc.local.' % self.serverName,
			addresses=['127.0.0.1'],
		)
		await self._zeroconf.async_register_service(oscInfo)


def OSCQueryHTTPServer_handler(root_node, host_info):
	async def handler(request):
		if request.method != 'GET':
			return web.Response(status=404, text='Invalid method')

		if request.url.path_qs == '/?HOST_INFO':
			return web.Response(text=str(host_info.to_json()), content_type='text/json')

		node = root_node.find_subnode(request.url.path_qs)
		if node is None:
			return web.Response(status=404, text='OSC Path not found')

		return web.Response(text=str(node.to_json()), content_type='text/json')

	return handler
