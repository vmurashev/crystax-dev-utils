#!/usr/bin/env python

import os
import os.path
import subprocess
import shlex
import tempfile

DIR_HERE=os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
with open(os.path.join(DIR_HERE, 'ndk.pth')) as ndklink:
    exec(ndklink.read())


MY_ABI = 'armeabi-v7a'
C_RUNTIME_DIR_FOR_MY_ABI = os.path.normpath(os.path.join(NDK_DIR, 'sources/crystax/libs/armeabi-v7a/thumb'))
C_RUNTIME_FOR_MY_ABI = os.path.join(C_RUNTIME_DIR_FOR_MY_ABI, 'libcrystax.so')
PYLIBS_TARGET_ROOT = '/data/local/tmp/pylibs'
PYLIBS_SRC_ROOT = os.path.normpath(os.path.join(NDK_DIR, 'sources/python/3.5/libs', MY_ABI))
TESTS_TARGET_ROOT = '/data/local/tmp/tests'
TESTS_SRC_ROOT = os.path.normpath(os.path.join(DIR_HERE, 'tests'))

INTERPRETER = \
'''#!/system/bin/sh
DIR_HERE=$(cd ${0%python} && pwd)
export LD_LIBRARY_PATH=$DIR_HERE/libs
exec $DIR_HERE/python.bin $*
'''


def check_call(cmdline):
	print("## COMMAND: {0}".format(cmdline))
	argv = shlex.split(cmdline)
	subprocess.check_call(argv)


def create_python_catolog():
	subdir_catalog = []
	file_catalog = []
	subdirs = [(PYLIBS_SRC_ROOT, '')]
	while subdirs:
		idx = len(subdirs) - 1
		src_pth, arc_pth = subdirs[idx]
		del subdirs[idx]
		for item in sorted(os.listdir(src_pth)):
			item_src_pth = os.path.join(src_pth, item)
			if arc_pth:
				item_arc_pth = '/'.join([arc_pth, item])
			else:
				item_arc_pth = item
			if os.path.isdir(item_src_pth):
				subdir_catalog.append(item_arc_pth)
				subdirs.append((item_src_pth, item_arc_pth))
			else:
				if item_arc_pth == 'python':
					item_arc_pth = 'python.bin'
				file_catalog.append((item_src_pth, item_arc_pth))
	return subdir_catalog, file_catalog


def adb_create_file_from_text(txt, dst_pth):
	fd, fname = tempfile.mkstemp()
	with os.fdopen(fd, "w") as fobj:
		fobj.write(txt)
	check_call('adb push {0} {1}'.format(fname, dst_pth))
	check_call('adb shell chmod 0777 {0}'.format(dst_pth))
	os.unlink(fname)


def main():
    # python
	check_call('adb shell rm -rf {0}'.format(PYLIBS_TARGET_ROOT))
	check_call('adb shell mkdir -p {0}'.format(PYLIBS_TARGET_ROOT))
	check_call('adb shell mkdir {0}/libs'.format(PYLIBS_TARGET_ROOT))
	check_call('adb push {0} {1}/libs'.format(C_RUNTIME_FOR_MY_ABI, PYLIBS_TARGET_ROOT))
	subdirs, files = create_python_catolog()
	for subdir in subdirs:
		check_call('adb shell mkdir {0}/{1}'.format(PYLIBS_TARGET_ROOT, subdir))
	for src_pth, arc_pth in files:
		check_call('adb push {0} {1}/{2}'.format(src_pth, PYLIBS_TARGET_ROOT, arc_pth))
	adb_create_file_from_text(INTERPRETER, '{0}/python'.format(PYLIBS_TARGET_ROOT))

    # tests
	check_call('adb shell rm -rf {0}'.format(TESTS_TARGET_ROOT))
	check_call('adb shell mkdir -p {0}'.format(TESTS_TARGET_ROOT))
	for item in sorted(os.listdir(TESTS_SRC_ROOT)):
		src_path = os.path.join(TESTS_SRC_ROOT, item)
		tgt_path = '{0}/{1}'.format(TESTS_TARGET_ROOT, item)
		check_call('adb push {0} {1}'.format(src_path, tgt_path))

	print("Done!")


if __name__ == '__main__':
	main()

