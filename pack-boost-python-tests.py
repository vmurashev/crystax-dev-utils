import argparse
import inspect
import os
import os.path
import json
import shutil
import tarfile


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


class GenException(Exception):
    def __init__(self, msg):
        frame = inspect.stack()[1]
        text = '[{}({})] {}'.format(os.path.basename(frame[1]), frame[2], msg)
        Exception.__init__(self, text)


def clean_dir(dname):
    if not os.path.isdir(dname):
        os.makedirs(dname)
    else:
        fsitems = os.listdir(dname)
        for item in fsitems:
            item_path = os.path.join(dname, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)


def copy_prebuilt_exe_to_dir(abi, src_dir, dst_dir):
    with open(os.path.join(src_dir, 'buildinfo.json')) as fh:
        exe_name = json.load(fh)['exe_name']
    src_file = os.path.join(src_dir, 'obj', 'local', abi, exe_name)
    dst_file = os.path.join(dst_dir, exe_name)
    shutil.copy(src_file, dst_file)
    return exe_name


def copy_prebuilt_pyd_to_dir(abi, src_dir, dst_dir):
    with open(os.path.join(src_dir, 'buildinfo.json')) as fh:
        pyd_name = json.load(fh)['pyd_name']
    src_file = os.path.join(src_dir, 'obj', 'local', abi, 'lib{}.so'.format(pyd_name))
    dst_file = os.path.join(dst_dir, '{}.so'.format(pyd_name))
    shutil.copy(src_file, dst_file)
    return pyd_name


def tar_dir_content(outdir, tar_file):
    catalog = []
    subdirs = [(outdir, '')]
    while subdirs:
        subdir_path, subdir_arcname = subdirs[0]
        del subdirs[0]
        for item in sorted(os.listdir(subdir_path)):
            item_path = os.path.join(subdir_path, item)
            if subdir_arcname:
                item_arcname = '/'.join([subdir_arcname, item])
            else:
                item_arcname = item
            if os.path.isdir(item_path):
                subdirs.append((item_path, item_arcname))
            else:
                catalog.append((item_path, item_arcname))

    with tarfile.open(tar_file, mode='w:gz') as th:
        for item_path, item_arcname in catalog:
            th.add(item_path, item_arcname)


def collect_boost_python_tests(target_python, objdir, abi, tar_file):
    print("Packaging Boost.Python tests(abi='{}') ...".format(abi))
    test_list_file = os.path.join(objdir, 'test-items.txt')
    with open(os.path.join(objdir, 'test-items.txt')) as fh:
        tests_names = [ ln.strip('\r\n').strip() for ln in fh.readlines() ]
    outdir = os.path.join(objdir, 'output-{}'.format(abi))
    clean_dir(outdir)
    shutil.copy(test_list_file, outdir)

    for tst_name in tests_names:
        description_file = os.path.join(objdir, tst_name, 'testinfo.json')
        with open(description_file) as fh:
            description = json.load(fh)
        action = description['mode']
        tst_dname_out = os.path.join(outdir, tst_name)
        os.makedirs(tst_dname_out)

        if action == 'run-exe':
            argv_files = description['argv_files']
            exe_link = description['exe_link']
            prebuilt_exe_dir = os.path.join(objdir, exe_link)
            exe_name = copy_prebuilt_exe_to_dir(abi, prebuilt_exe_dir, tst_dname_out)
            argv = []
            for arg_file in argv_files:
                arg_name = os.path.basename(arg_file)
                shutil.copy(arg_file, os.path.join(tst_dname_out, arg_name))
                argv.append(arg_name)

            final_description = json.dumps({
                'exe_name': './{}'.format(exe_name),
                'cwd-here': True,
                'argv': argv,
            })

            final_description_file = os.path.join(tst_dname_out, 'testconfig.json')
            with open(final_description_file, mode='wt') as fh:
                fh.write(final_description)

        elif action == 'run-py':
            pyd_links = description['pyd_links']
            py_scripts = description['py_scripts']
            py_main_script = description['py_main_script']
            for pydlnk in pyd_links:
                prebuilt_so_dir = os.path.join(objdir, pydlnk)
                copy_prebuilt_pyd_to_dir(abi, prebuilt_so_dir, tst_dname_out)

            py_main_file_name = os.path.basename(py_main_script)
            shutil.copy(py_main_script, os.path.join(tst_dname_out, py_main_file_name))

            py_names = []
            for pyfile in py_scripts:
                pyfile_name = os.path.basename(pyfile)
                shutil.copy(pyfile, os.path.join(tst_dname_out, pyfile_name))
                py_names.append(pyfile_name)

            final_description = json.dumps({
                'exe_name': target_python,
                'cwd-here': True,
                'argv': [py_main_file_name],
            })

            final_description_file = os.path.join(tst_dname_out, 'testconfig.json')
            with open(final_description_file, mode='wt') as fh:
                fh.write(final_description)

        else:
            raise GenException("Unexpected test mode '{}' is given in file '{}'".format(action, description_file))

    tar_dir_content(outdir, tar_file)
    print("Boost.Python tests(abi='{}') are in file '{}'".format(abi, tar_file))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target-python', required=True)
    parser.add_argument('--objdir', required=True)
    parser.add_argument('--abi', choices=SUPPORTED_ABI, required=True)
    parser.add_argument('--tgzout', required=True)
    args = parser.parse_args()
    try:
        collect_boost_python_tests(args.target_python, args.objdir, args.abi, os.path.normpath(os.path.abspath(args.tgzout)))
    except GenException as ex:
        print("ERROR: {}".format(ex))
        exit(126)
