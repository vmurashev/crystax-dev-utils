import argparse
import os
import os.path
import inspect
import shutil


JAM_SIMPLE_INSTRUCTIONS = ['import', 'lib', 'use-project', 'project', 'local', 'test-suite']
JAM_COMPLEX_INSTRUCTIONS = ['if', 'rule']
TEST_OPS_TO_SKIP = ['compile', 'py-compile', 'py-compile-fail']
KNOWN_TEST_TYPES = ['run', 'bpl-test', 'py-run', 'python-extension']

NDK_BOOST_VERSION = '1.61.0'


class GenException(Exception):
    def __init__(self, msg):
        frame = inspect.stack()[1]
        text = '[{}({})] {}'.format(os.path.basename(frame[1]), frame[2], msg)
        Exception.__init__(self, text)


class BoostPythonTest_Run:
    def __init__(self, *, short_name, jamfile, jamline, arg_list_files, exe_from_depends):
        self.jamfile = jamfile
        self.jamline = jamline
        self.exe_from_depends = exe_from_depends
        self.arg_list_files = arg_list_files
        print("!{:20}## exe={} ## argv={}".format('TEST(RUN)-{}'.format(short_name), exe_from_depends, arg_list_files))


class BoostPythonTest_PyScript:
    def __init__(self, *, short_name, jamfile, jamline, py_scripts, depends):
        self.jamfile = jamfile
        self.jamline = jamline
        self.depends = depends
        self.py_scripts = py_scripts
        print("!{:20}## py_scripts={} ## depends={}".format('TEST(PYD)-{}'.format(short_name), py_scripts, depends))


def write_text_lines_in_file(fname, text_list):
    with open(fname, mode='wt') as fh:
        for ln in text_list:
            fh.writelines([ln, '\n'])


class BuildContext:
    def __init__(self, build_root,*, py2):
        self._build_root = os.path.normpath(os.path.abspath(build_root))
        self._is_py2 = py2

    def get_build_root(self):
        return self._build_root

    def generate_android_mk_for_executable(self, *, exe_name, sources, jni_dir):
        text_list = [
            'include $(CLEAR_VARS)',
            'LOCAL_PATH := $(call my-dir)',
            'LOCAL_MODULE := {}'.format(exe_name),
            'LOCAL_SRC_FILES := \\',
        ]

        idx = 0
        for src in sources:
            idx += 1
            if idx < len(sources):
                text_list += [ '    {} \\'.format(src)]
            else:
                text_list += [ '    {}'.format(src)]

        if self._is_py2:
            text_list += [
                'LOCAL_STATIC_LIBRARIES := python_shared boost_python_static'
            ]
        else:
            text_list += [
                'LOCAL_STATIC_LIBRARIES := python_shared boost_python3_static'
            ]

        text_list += [
            'LOCAL_LDLIBS := -lz',
            'include $(BUILD_EXECUTABLE)',
        ]

        if self._is_py2:
            text_list += [
                '$(call import-module,python/2.7)',
            ]
        else:
            text_list += [
                '$(call import-module,python/3.5)',
            ]

        text_list += [
            '$(call import-module,boost/{})'.format(NDK_BOOST_VERSION),
        ]

        android_mk = os.path.join(jni_dir, 'Android.mk')
        write_text_lines_in_file(android_mk, text_list)


    def generate_android_mk_for_python_module(self, *, pyd_name, sources, jni_dir):
        text_list = [
            'include $(CLEAR_VARS)',
            'LOCAL_PATH := $(call my-dir)',
            'LOCAL_MODULE := {}'.format(pyd_name),
            'LOCAL_SRC_FILES := \\',
        ]

        idx = 0
        for src in sources:
            idx += 1
            if idx < len(sources):
                text_list += [ '    {} \\'.format(src)]
            else:
                text_list += [ '    {}'.format(src)]

        if self._is_py2:
            text_list += [
                'LOCAL_STATIC_LIBRARIES := python_shared boost_python_static'
            ]
        else:
            text_list += [
                'LOCAL_STATIC_LIBRARIES := python_shared boost_python3_static'
            ]

        text_list += [
            'LOCAL_LDLIBS := -lz',
            'include $(BUILD_SHARED_LIBRARY)',
        ]

        if self._is_py2:
            text_list += [
                '$(call import-module,python/2.7)',
            ]
        else:
            text_list += [
                '$(call import-module,python/3.5)',
            ]

        text_list += [
            '$(call import-module,boost/{})'.format(NDK_BOOST_VERSION),
        ]

        android_mk = os.path.join(jni_dir, 'Android.mk')
        write_text_lines_in_file(android_mk, text_list)


class BuildItem:
    def __init__(self, *, short_name, jamfile, jamline, build_list_files, pyext_name):
        self.short_name = short_name
        self.jamfile = jamfile
        self.jamline = jamline
        self.build_list = build_list_files
        self.pyext_name = pyext_name
        print("!{:20}## pyext = {} ## build_list={}".format('BUILD-{}'.format(short_name), pyext_name, build_list_files))
        if not build_list_files:
            raise GenException("Can't parse '{}' - got empty build list at line {}".format(jamfile, jamline))

    def generate(self, ctx):
        jamdir = os.path.normpath(os.path.abspath(os.path.dirname(self.jamfile)))
        sources = []
        for src in self.build_list:
            src_path = os.path.normpath(os.path.abspath(os.path.join(jamdir, src)))
            if not os.path.isfile(src_path):
                raise GenException("Can't parse '{}' at line {} - file not found: '{}' ".format(self.jamfile, self.jamline, src_path))
            sources.append(src_path)
        jni_dir = os.path.join(ctx.get_build_root(), self.short_name, 'jni')
        os.makedirs(jni_dir, exist_ok=True)

        if self.pyext_name is None:
            exe_name = os.path.splitext(os.path.basename(sources[0]))[0]
            ctx.generate_android_mk_for_executable(exe_name=exe_name, sources=sources, jni_dir=jni_dir)
        else:
            ctx.generate_android_mk_for_python_module(pyd_name=self.pyext_name, sources=sources, jni_dir=jni_dir)

    def get_test_short_name(self):
        return self.short_name


def get_tokens_from_section(section_index, tokens):
    result = []
    current_section = 0
    for tk in tokens:
        if tk == ':':
            current_section +=1
            continue
        elif current_section == section_index:
            result.append(tk)
        elif current_section > section_index:
            break
    return result


def parse_boost_python_jamfile(jamfname, naming_offset, tests, builds):
    jamfile = os.path.normpath(os.path.abspath(jamfname))
    lines = [line.rstrip('\r\n') for line in open(jamfile)]
    tokens = []
    lnnum = 0
    for ln in lines:
        lnnum += 1
        cmnt_pos = ln.find('#')
        if cmnt_pos < 0:
            line = ln
        else:
            line = ln[0:cmnt_pos]
        line = line.strip()
        if not line:
            continue
        for tk in line.split():
            tokens.append((tk, lnnum))
    instructions = []
    instruction = []
    complex_mode = False
    depth = 0
    for tk, lnnum in tokens:
        if not instruction:
            if (tk not in JAM_SIMPLE_INSTRUCTIONS) and (tk not in JAM_COMPLEX_INSTRUCTIONS):
                raise GenException("Can't parse '{}' - got unknown instruction: '{}' at line {}".format(jamfile, tk, lnnum))
        if not complex_mode and tk in ['if', 'rule']:
            complex_mode = True
        instruction.append((tk, lnnum))
        if complex_mode:
            if tk == '{':
                depth += 1
            elif tk == '}':
                depth -= 1
                if depth == 0:
                    complex_mode = False
                    instructions.append(instruction)
                    instruction = []
        else:
            if tk == ';':
                instructions.append(instruction)
                instruction = []
    if instruction:
        raise GenException("Can't parse '{}' - instruction not finished: {}".format(jamfile, ' '.join(instruction)))

    suits = []
    for i in instructions:
        if i[0][0] == 'test-suite':
            suit = []
            if i[2][0] != ':':
                raise GenException("Can't parse '{}' - got unexpected instruction '{}' at line {}".format(jamfile, i[2][0], i[2][1]))
            depth = 0
            for tk, lnnum in i[3:len(i)-1]:
                if tk == '[':
                    if depth != 0:
                        raise GenException("Failed to parse '{}' - stopped at line {}".format(jamfile, lnnum))
                    depth += 1
                elif tk == ']':
                    depth -= 1
                    if depth != 0:
                        raise GenException("Failed to parse '{}' - stopped at line {}".format(jamfile, lnnum))
                    if suit[0][0] not in TEST_OPS_TO_SKIP:
                        suits.append(suit)
                    suit = []
                else:
                    suit.append((tk, lnnum))

    entries = []
    suits_set = set()
    for s in suits:
        action = s[0][0]
        lnnum1 = s[0][1]
        if action not in KNOWN_TEST_TYPES:
            raise GenException("Can't parse '{}' - got unknown type of test '{}' at line {}".format(jamfile, action, lnnum1))
        x = []
        windows_only = False
        for tk, lnnum in s:
            if '<conditional>@require-windows' in tk:
                windows_only = True
            if ('<' in tk) or ('>' in tk) or ('$' in tk) or ('exec-dynamic' in tk) or ('/python/' in tk):
                continue
            x.append(tk)
        for i in range(len(x)-1,-1,-1):
            if x[i] == ':':
                del x[i]
            else:
                break
        if windows_only:
            continue
        as_text = ' '.join(x)
        if as_text in suits_set:
            continue
        suits_set.add(as_text)
        entries.append((x, lnnum1))

    processed_python_extensions = {}
    idx = naming_offset
    for entry, lnnum in entries:
        idx += 1
        build_name = 'b{}'.format(idx)
        test_name  = 't{}'.format(idx)

        if entry[0] == 'python-extension':
            section0 = get_tokens_from_section(0, entry[1:])
            if (len(section0)) != 1:
                raise GenException("Failed to parse '{}' - stopped at line {}".format(jamfile, lnnum))
            build_list_files = get_tokens_from_section(1, entry)

            builds.append(BuildItem(
                short_name=build_name,
                build_list_files=build_list_files,
                pyext_name=section0[0],
                jamfile=jamfile,
                jamline=lnnum))

            processed_python_extensions[section0[0]] = build_name

        elif entry[0] == 'run' or entry[0] == 'py-run':
            build_list_files = get_tokens_from_section(0, entry[1:])
            arg_list_files = get_tokens_from_section(2, entry[1:])

            builds.append(BuildItem(
                short_name=build_name,
                build_list_files=build_list_files,
                pyext_name=None,
                jamfile=jamfile,
                jamline=lnnum))

            tests.append(BoostPythonTest_Run(
                short_name=test_name,
                arg_list_files=arg_list_files,
                exe_from_depends=build_name,
                jamfile=jamfile,
                jamline=lnnum))

        elif entry[0] == 'bpl-test':
            section0 = get_tokens_from_section(0, entry[1:])
            if (len(section0)) != 1:
                raise GenException("Failed to parse '{}' - stopped at line {}".format(jamfile, lnnum))

            bpl_id = section0[0]
            depends = get_tokens_from_section(1, entry[1:])
            if not depends:
                builds.append(BuildItem(
                    short_name=build_name,
                    build_list_files=['{}.cpp'.format(bpl_id)],
                    pyext_name='{}_ext'.format(bpl_id),
                    jamfile=jamfile,
                    jamline=lnnum))

                tests.append(BoostPythonTest_PyScript(
                    short_name=test_name,
                    py_scripts=['{}.py'.format(bpl_id)],
                    depends=[build_name],
                    jamfile=jamfile,
                    jamline=lnnum))
            else:
                py_scripts = []
                build_list = []
                py_ext_deps = []
                for dep in depends:
                    if dep.endswith('.cpp'):
                        build_list.append(dep)
                    elif dep.endswith('.py'):
                        py_scripts.append(dep)
                    elif dep in processed_python_extensions:
                        py_ext_deps.append(processed_python_extensions[dep])
                    else:
                        raise GenException("Can't parse '{}' - got unknown token '{}' at line {}".format(jamfile, dep, lnnum))
                if not build_list and not py_ext_deps:
                    raise GenException("Failed to parse '{}' - stopped at line {}".format(jamfile, lnnum))
                if not py_scripts:
                    raise GenException("Failed to parse '{}' - stopped at line {}".format(jamfile, lnnum))

                dep_names = []
                source_idx = 0
                for source in build_list:
                    source_idx += 1
                    if len(build_list) == 1:
                        dep_name = build_name
                    else:
                        dep_name = '{}-x{}'.format(build_name, source_idx)
                    dep_names.append(dep_name)
                    builds.append(BuildItem(
                        short_name=dep_name,
                        build_list_files=[source],
                        pyext_name=os.path.splitext(os.path.basename(source))[0],
                        jamfile=jamfile,
                        jamline=lnnum))

                tests.append(BoostPythonTest_PyScript(
                    short_name=test_name,
                    py_scripts=py_scripts,
                    depends=dep_names + py_ext_deps,
                    jamfile=jamfile,
                    jamline=lnnum))
        else:
            raise GenException("Can't parse '{}' - got unknown type of test '{}' at line {}".format(jamfile, entry[0], lnnum))


def clean_dir(dname):
    fsitems = os.listdir(dname)
    for item in fsitems:
        item_path = os.path.join(dname, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)


def generate_boost_python_tests(jamfiles, objdir_py2, objdir_py3):
    if not jamfiles:
        raise Exception("List of jamfiles can't be empty")
    if not objdir_py2 and not objdir_py3:
        raise Exception("At list one obj directory must be specified")

    tests = []
    builds = []
    naming_offset = 0
    for j in jamfiles:
        naming_offset += 1000
        parse_boost_python_jamfile(j, naming_offset, tests, builds)
    if not tests:
        raise GenException("Cannot find any boost-python test in specified jamfiles: {0}".format(jamfiles))

    print("Got {0} boost-python tests from specified jamfiles".format(len(tests)))
    print("Got {0} build items from specified jamfiles".format(len(builds)))

    ctx2 = None
    ctx3 = None
    if objdir_py2:
        clean_dir(objdir_py2)
        ctx2 = BuildContext(objdir_py2, py2=True)
    if objdir_py3:
        clean_dir(objdir_py3)
        ctx3 = BuildContext(objdir_py3, py2=False)

    build_names2 = []
    build_names3 = []
    for build_item in builds:
        if ctx2:
            build_item.generate(ctx2)
            build_name = build_item.get_test_short_name()
            build_names2.append(build_name)
        if ctx3:
            build_item.generate(ctx3)
            build_name = build_item.get_test_short_name()
            build_names3.append(build_name)

    if build_names2:
        build_info2 = os.path.join(objdir_py2, 'build-items.txt')
        write_text_lines_in_file(build_info2, build_names2)

    if build_names3:
        build_info3 = os.path.join(objdir_py3, 'build-items.txt')
        write_text_lines_in_file(build_info3, build_names3)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--jamfiles', nargs='*')
    parser.add_argument('--objdir-py2')
    parser.add_argument('--objdir-py3')
    args = parser.parse_args()
    try:
        generate_boost_python_tests(args.jamfiles, args.objdir_py2, args.objdir_py3)
    except GenException as ex:
        print("ERROR: {}".format(ex))
        exit(126)
