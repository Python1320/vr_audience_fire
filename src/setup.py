from cx_Freeze import setup, Executable

packages = ['pythonosc', 'psutil', 'zeroconf', 'json', 'threading', 'time', 'os', 'sys', 'ctypes', 'traceback']
file_include = ['config.json', 'app.vrmanifest']

build_exe_options = {
	'packages': packages,
	'include_files': file_include,
	'include_msvcr': False,
	'optimize': 0,
}

setup(
	name='vr_audience_fire',
	version='0.2',
	description='Lets you catch on fire',
	options={'build_exe': build_exe_options},
	executables=[
		Executable('main.py', target_name='vr_audience_fire.exe', base='console', icon='../icon.ico'),
		Executable('main.py', target_name='vr_audience_fire_NoConsole.exe', base='Win32GUI', icon='../icon.ico'),
	],
)
