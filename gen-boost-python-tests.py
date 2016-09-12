import argparse
import os.path
import inspect


JAM_SIMPLE_INSTRUCTIONS = ['import', 'lib', 'use-project', 'project', 'local', 'test-suite']
JAM_COMPLEX_INSTRUCTIONS = ['if', 'rule']
TEST_OPS_TO_SKIP = ['compile', 'py-compile', 'py-compile-fail']
KNOWN_TEST_TYPES = ['run', 'bpl-test', 'py-run', 'python-extension']


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


class BuildContext:
    def __init__(self, obj_root):
        self._obj_root = obj_root


class BuildItem:
    def __init__(self, *, short_name, jamfile, jamline, build_list_files, pyext_name):
        self.short_name = short_name
        self.jamfile = jamfile
        self.jamline = jamline
        self.build_list_files = build_list_files
        print("!{:20}## pyext = {} ## build_list={}".format('BUILD-{}'.format(short_name), pyext_name, build_list_files))

    def generate(self, ctx):
        pass

    def get_test_short_name(self):
        pass

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
        for tk, lnnum in s:
            if ('<' in tk) or ('>' in tk) or ('$' in tk) or ('exec-dynamic' in tk) or ('/python/' in tk):
                continue
            x.append(tk)
        for i in range(len(x)-1,-1,-1):
            if x[i] == ':':
                del x[i]
            else:
                break
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

#    ctx2 = None
#    ctx3 = None
#    if objdir_py2:
#        ctx2 = BuildContext(objdir_py2)
#    if objdir_py3:
#        ctx3 = BuildContext(objdir_py3)

#    names2 = []
#    names3 = []
#    for tst in tests:
#        if ctx2:
#            tst.generate(ctx2)
#            tst_name = tst.get_test_short_name()
#            names2.append(tst_name)
#        if ctx3:
#            tst.generate(ctx3)
#            tst_name = tst.get_test_short_name()
#            names3.append(tst_name)

    raise GenException("TODO - Generate tests list")



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
        exit(1)
