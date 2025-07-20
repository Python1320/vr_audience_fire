from cx_Freeze import setup, Executable
import shutil

packages = ['pythonosc', 'psutil', 'zeroconf', 'json', 'threading', 'time', 'os', 'sys', 'ctypes', 'traceback']
file_include = ['config.json', 'app.vrmanifest']

build_exe_options = {
	'packages': packages,
	'include_files': file_include,
	'include_msvcr': False,
	'optimize': 0,
	'build_exe': '../vr_audience_fire_helper',
}

setup(
	name='vr_audience_fire',
	version='0.2',
	description='vr_audience_fire.exe: A chance of catching on fire',
	options={'build_exe': build_exe_options},
	executables=[
		Executable('main.py', target_name='vr_audience_fire.exe', base='Win32GUI', icon='../icon.ico'),
		Executable('main.py', target_name='vr_audience_fire_console.exe', base='console', icon='../icon.ico'),
	],
)


shutil.make_archive('../vr_audience_fire_helper', 'zip', '../vr_audience_fire_helper')
