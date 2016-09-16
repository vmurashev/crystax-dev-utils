import argparse
import inspect
import os
import os.path
import json
import subprocess
import datetime


TESTCFG_FNAME_DEFAULT = 'testconfig.json'

TAG_TESTCGF_EXE_HERE = 'exe-here'
TAG_TESTCGF_CWD_HERE = 'cwd-here'
TAG_TESTCGF_EXE_NAME = 'executable'
TAG_TESTCGF_ARGV     = 'argv'


class GenException(Exception):
    def __init__(self, msg):
        frame = inspect.stack()[1]
        text = '[{}({})] {}'.format(os.path.basename(frame[1]), frame[2], msg)
        Exception.__init__(self, text)


def log_message(msg, log):
    print(msg)
    print(msg, file=log)


class TestFixture:
    def __init__(self, title, dname_with_test, config):
        self.title = title
        self.dname_with_test = dname_with_test
        self.exe_here = config.get(TAG_TESTCGF_EXE_HERE, False)
        self.cwd_here = config.get(TAG_TESTCGF_CWD_HERE, False)
        self.executable = config[TAG_TESTCGF_EXE_NAME]
        self.argv = config.get(TAG_TESTCGF_ARGV, [])

    def perform(self, *, log):
        log_message(">>> {}".format(self.title), log)
        cwd = None
        exe = None
        exit_code = None

        if self.cwd_here:
            cwd = self.dname_with_test

        if self.exe_here:
            exe = os.path.normpath(os.path.join(self.dname_with_test, self.executable))
        else:
            exe = self.executable

        argv = [exe] + self.argv
        cmdline = ' '.join([self.executable] + self.argv)
        log_message("> {}".format(cmdline), log)
        try:
            child = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            output, _ = child.communicate()
            exit_code = child.returncode
        except Exception as ex:
            output = str(ex)
        for ln in output.splitlines():
            if exit_code is None:
                log_message("! {}".format(ln), log)
            else:
                log_message(ln, log)
        if exit_code is not None:
            log_message("$? = {}".format(exit_code), log)

        return cmdline, exit_code, output


def collect_test_configs(dir_list_from_text_file):
    file_with_tests_list = os.path.normpath(os.path.abspath(dir_list_from_text_file))
    if not os.path.isfile(file_with_tests_list):
        raise GenException("File not found: '{}'".format(file_with_tests_list))
    with open(file_with_tests_list) as fh:
        tests_names = [txt for txt in filter(lambda x: x and not x.startswith('#'), [ ln.strip('\r\n').strip() for ln in fh.readlines() ]) ]
    if not tests_names:
        raise GenException("Can't find any test links in file: '{}'".format(file_with_tests_list))
    catalog = []
    for test_link in tests_names:
        dname_with_test = os.path.normpath(os.path.join(os.path.dirname(file_with_tests_list), test_link))
        file_with_test_config = os.path.join(dname_with_test, TESTCFG_FNAME_DEFAULT)
        if not os.path.isfile(file_with_test_config):
            raise GenException("Config file not found: '{}'".format(file_with_test_config))
        with open(file_with_test_config) as fh:
            try:
                cfg = json.load(fh)
                test = TestFixture(test_link, dname_with_test, cfg)
                catalog.append(test)
            except Exception as ex:
                raise GenException("Got malformed config: '{}', {}: {}".format(file_with_test_config, type(ex), ex))
    return catalog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir-list-from-text-file', required=True)
    args = parser.parse_args()
    tests = collect_test_configs(args.dir_list_from_text_file)
    time_txt = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    log_fpath = os.path.normpath(os.path.abspath(os.path.join('tests-exec-{}.log'.format(time_txt))))
    with open(log_fpath, mode='wt') as log:
        total  = 0
        passed = 0
        log_message("* Loaded {} test(s)".format(len(tests)), log)
        for test in tests:
            cmdline, retcode, output = test.perform(log=log)
            total += 1
            if isinstance(retcode, int):
                if retcode == 0:
                    passed += 1
        log_message("* Done: passed={}, failed={}, total={}".format(passed, total - passed, total), log)
    print("Logged in: '{}'".format(log_fpath))

if __name__ == '__main__':
    try:
        main()
    except GenException as ex:
        print("ERROR: {}".format(ex))
        exit(126)
