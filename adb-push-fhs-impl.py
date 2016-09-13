import os
import os.path
import subprocess
import shlex
import tempfile
import sys
import inspect

PYTHON2_ABI = '2.7'
PYTHON3_ABI = '3.5'

SUPPORTED_ABI=(
    'armeabi',
    'armeabi-v7a',
    'armeabi-v7a-hard',
    'arm64-v8a',
    'x86',
    'x86_64',
    'mips',
    'mips64',
)

DIR_HERE=os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
with open(os.path.join(DIR_HERE, 'ndk.pth')) as ndklink:
    exec(ndklink.read())

DIR_SRC_CRYSTAX = os.path.normpath(os.path.join(NDK_DIR, 'sources/crystax/libs'))
DIR_SRC_CXXSTL  = os.path.normpath(os.path.join(NDK_DIR, 'sources/cxx-stl/gnu-libstdc++/5/libs'))
DIR_SRC_PYTHON2 = os.path.normpath(os.path.join(NDK_DIR, 'sources/python/{}/shared'.format(PYTHON2_ABI)))
DIR_SRC_PYTHON3 = os.path.normpath(os.path.join(NDK_DIR, 'sources/python/{}/shared'.format(PYTHON3_ABI)))

DIR_TARGET_ROOT = '/data/local/tmp'
DIR_TARGET_FSH_ROOT = '/'.join([DIR_TARGET_ROOT, 'fhs'])
DIR_TARGET_LIB = '/'.join([DIR_TARGET_FSH_ROOT, 'lib'])
DIR_TARGET_BIN = '/'.join([DIR_TARGET_FSH_ROOT, 'bin'])


class GenException(Exception):
    def __init__(self, msg):
        frame = inspect.stack()[1]
        text = '[{}({})] {}'.format(os.path.basename(frame[1]), frame[2], msg)
        Exception.__init__(self, text)


def check_call(cmdline):
    print("## COMMAND: {0}".format(cmdline))
    argv = shlex.split(cmdline)
    subprocess.check_call(argv)


def check_output(cmdline):
    print("## COMMAND: {0}".format(cmdline))
    argv = shlex.split(cmdline)
    return subprocess.check_output(argv, universal_newlines=True).rstrip('\r\n').strip()


def create_python_catolog(abi):
    subdir_catalog = []
    file_catalog = []
    for pysrc_dir, py_dname in [(DIR_SRC_PYTHON2, 'python{}'.format(PYTHON2_ABI)), (DIR_SRC_PYTHON3, 'python{}'.format(PYTHON3_ABI))]:
        subdirs = [(os.path.join(pysrc_dir, abi), '')]
        while subdirs:
            idx = len(subdirs) - 1
            src_pth, arc_pth = subdirs[idx]
            del subdirs[idx]
            for item in sorted(os.listdir(src_pth)):
                in_libs = False
                if not arc_pth and item == 'libs':
                    in_libs = True
                item_src_pth = os.path.join(src_pth, item)
                if arc_pth:
                    item_arc_pth = '/'.join([arc_pth, item])
                else:
                    if item == 'libs':
                        item_arc_pth = DIR_TARGET_LIB
                    else:
                        item_arc_pth = '/'.join([DIR_TARGET_BIN, py_dname, item])
                if os.path.isdir(item_src_pth):
                    if item_arc_pth != DIR_TARGET_LIB:
                        subdir_catalog.append(item_arc_pth)
                    subdirs.append((item_src_pth, item_arc_pth))
                else:
                    file_catalog.append((item_src_pth, item_arc_pth))
    return subdir_catalog, file_catalog


def main():
    abi = check_output("adb shell getprop ro.product.cpu.abi")
    if abi not in SUPPORTED_ABI:
        raise GenException("Unknown CPU ABI: '{}'".format(abi))
    print("## CPU ABI: {}".format(abi))

    check_call('adb shell rm -rf {}'.format(DIR_TARGET_FSH_ROOT))
    check_call('adb push {} {}'.format(os.path.join(DIR_HERE, 'shell.sh'), '/'.join([DIR_TARGET_ROOT, 'shell.sh'])))
    check_call('adb shell mkdir -p {}'.format(DIR_TARGET_LIB))
    check_call('adb shell mkdir -p {}'.format(DIR_TARGET_BIN))

    check_call('adb push {} {}'.format(os.path.join(DIR_SRC_CRYSTAX, abi, 'libcrystax.so'), '/'.join([DIR_TARGET_LIB, 'libcrystax.so'])))
    check_call('adb push {} {}'.format(os.path.join(DIR_SRC_CXXSTL, abi, 'libgnustl_shared.so'), '/'.join([DIR_TARGET_LIB, 'libgnustl_shared.so'])))

    py_dirs, py_files = create_python_catolog(abi)
    for dname in py_dirs:
        check_call('adb shell mkdir -p {}'.format(dname))
    for py_src, py_dst in py_files:
        check_call('adb push {} {}'.format(py_src, py_dst))
    check_call('adb shell cd {} && ln -s python{}/python python2'.format(DIR_TARGET_BIN, PYTHON2_ABI))
    check_call('adb shell cd {} && ln -s python{}/python python3'.format(DIR_TARGET_BIN, PYTHON3_ABI))


if __name__ == '__main__':
    try:
        main()
    except GenException as ex:
        print("ERROR: {}".format(ex))
        exit(126)
