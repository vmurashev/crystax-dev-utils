import argparse
import inspect
import os
import os.path
import json
import subprocess
import traceback
import sys

TEST_EXEC_TIMEOUT     = 60 # seconds
TESTCFG_FNAME_DEFAULT = 'testconfig.json'
TESTCFG_FNAME_OUTPUT  = 'testconfig.output'

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
    print(msg, flush=True)
    if log is not None:
        print(msg, file=log, flush=True)


class TestFixture:
    def __init__(self, title, dname_with_test, config):
        self._title = title
        self._dname_with_test = dname_with_test
        self._exe_here = config.get(TAG_TESTCGF_EXE_HERE, False)
        self._cwd_here = config.get(TAG_TESTCGF_CWD_HERE, False)
        self._executable = config[TAG_TESTCGF_EXE_NAME]
        self._argv = config.get(TAG_TESTCGF_ARGV, [])


    @staticmethod
    def load(title, dname_with_test, cfg_fname):
        cfg = None
        with open(cfg_fname) as fh:
            try:
                cfg = json.load(fh)
            except Exception:
                traceback.print_exc(file=sys.stdout)
        if cfg is None:
            raise GenException("Got malformed config: '{}'".format(cfg_fname))
        return TestFixture(title, dname_with_test, cfg)

    @property
    def title(self):
        return self._title

    def perform(self, *, log):
        log_message(">>> {}".format(self._title), log)

        cwd = None
        exe = None
        exit_code = None
        timed_out = False
        sigint = False

        if self._cwd_here:
            cwd = self._dname_with_test

        if self._exe_here:
            exe = os.path.normpath(os.path.join(self._dname_with_test, self._executable))
        else:
            exe = self._executable

        argv = [exe] + self._argv
        cmdline = ' '.join([self._executable] + self._argv)
        log_message("> {}".format(cmdline), log)
        child = None
        output = ''
        output_fpath = os.path.join(self._dname_with_test, TESTCFG_FNAME_OUTPUT)
        try:
            with open(output_fpath, 'wb') as fout:
                child = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=fout, stderr=fout)
                child.communicate(timeout=TEST_EXEC_TIMEOUT)
                exit_code = child.returncode
            with open (output_fpath, "rt") as fout:
                output = fout.read()
        except subprocess.TimeoutExpired:
            child.kill()
            child.communicate()
            output = 'HUNG'
            timed_out = True
        except KeyboardInterrupt:
            child.kill()
            child.communicate()
            output = 'KeyboardInterrupt'
            sigint = True
        except Exception as ex:
            output = str(ex)

        for ln in output.splitlines():
            if exit_code is None:
                log_message("! {}".format(ln), log)
            else:
                log_message(ln, log)

        if exit_code is not None:
            log_message("$? = {}".format(exit_code), log)

        return cmdline, exit_code, output, timed_out, sigint


def collect_test_configs(dir_list_from_text_file, catalog):
    file_with_tests_list = os.path.normpath(os.path.abspath(dir_list_from_text_file))
    if not os.path.isfile(file_with_tests_list):
        raise GenException("File not found: '{}'".format(file_with_tests_list))
    with open(file_with_tests_list) as fh:
        tests_names = [txt for txt in filter(lambda x: x and not x.startswith('#'), [ ln.strip('\r\n').strip() for ln in fh.readlines() ]) ]
    if not tests_names:
        raise GenException("Can't find any test links in file: '{}'".format(file_with_tests_list))
    for test_link in tests_names:
        dname_with_test = os.path.normpath(os.path.join(os.path.dirname(file_with_tests_list), test_link))
        file_with_test_config = os.path.join(dname_with_test, TESTCFG_FNAME_DEFAULT)
        if not os.path.isfile(file_with_test_config):
            raise GenException("Config file not found: '{}'".format(file_with_test_config))
        test = TestFixture.load(test_link, dname_with_test, file_with_test_config)
        catalog.append(test)


def collect_one_test(test_link, catalog):
    dname_with_test = os.path.normpath(os.path.abspath(test_link))
    file_with_test_config = os.path.join(dname_with_test, TESTCFG_FNAME_DEFAULT)
    if not os.path.isfile(file_with_test_config):
        raise GenException("Config file not found: '{}'".format(file_with_test_config))
    test = TestFixture.load(test_link, dname_with_test, file_with_test_config)
    catalog.append(test)


def run_loaded_tests(tests, log):
    total  = 0
    passed = 0
    failed = 0
    hung_cache = []
    failed_names = []

    log_message("* Loaded {} test(s)".format(len(tests)), log)
    work_list = tests[:]
    while work_list:
        for test in work_list:
            cmdline, retcode, output, timed_out, sigint = test.perform(log=log)
            if sigint:
                break
            total += 1
            if isinstance(retcode, int) and retcode == 0:
                passed += 1
            elif timed_out:
                hung_cache.append(test)
            else:
                failed += 1
                failed_names.append(test.title)
        work_list = hung_cache[:]
        hung_cache = []

    log_message("* DONE: passed={}, failed={}, total={}".format(passed, failed, total), log)
    if failed_names:
        log_message("* FAILED: {}".format(', '.join(failed_names)), log)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dlist')
    parser.add_argument('--one')
    parser.add_argument('--log')
    args = parser.parse_args()

    tests = []
    if args.dlist is not None:
        collect_test_configs(args.dlist, tests)

    if args.one is not None:
        collect_one_test(args.one, tests)

    if not tests:
        parser.print_help()
        return

    log_fpath = None
    log_fh = None
    if args.log is not None:
        log_fpath = os.path.normpath(os.path.abspath(args.log))
        log_fh = open(log_fpath, mode='wt')

    run_loaded_tests(tests, log_fh)

    if log_fh is not None:
        log_fh.close()
        print("Logged in: '{}'".format(log_fpath))

if __name__ == '__main__':
    try:
        main()
    except GenException as ex:
        print("ERROR: {}".format(ex))
        exit(126)
