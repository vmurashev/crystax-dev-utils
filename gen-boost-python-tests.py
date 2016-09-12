import argparse
import os.path

JAM_SIMPLE_INSTRUCTIONS = ['import', 'lib', 'use-project', 'project', 'local', 'test-suite']
JAM_COMPLEX_INSTRUCTIONS = ['if', 'rule']
TEST_OPS_TO_SKIP = ['compile', 'py-compile', 'py-compile-fail']
KNOWN_TEST_TYPES = ['run', 'bpl-test', 'py-run', 'python-extension']


class GenException(Exception):
    pass


class BuildContext:
    def __init__(self, obj_root):
        self._obj_root = obj_root


class BoostPythonTest_Run:
    def __init__(self, *, short_name, jamfile, jamline, arg_list_files, depends):
        self.arg_list_files = arg_list_files
        self.depends = depends
        print("arg_list_files={}".format(arg_list_files))


class BuildItem:
    def __init__(self, *, short_name, jamfile, jamline, build_list_files, pyext_name=None):
        self.short_name = short_name
        self.jamfile = jamfile
        self.jamline = jamline
        self.build_list_files = build_list_files
        print(80*'-')
        print(short_name)
        print(80*'-')
        print("pyext_name={}".format(pyext_name))
        print("build_list_files={}".format(build_list_files))

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

    idx = naming_offset
    for entry, lnnum in entries:
        idx += 1
        build_name = 'b{}'.format(idx)
        test_name  = 't{}'.format(idx)

        if entry[0] == 'python-extension':
            build_list_files = get_tokens_from_section(1, entry)

            builds.append(BuildItem(
                short_name=build_name,
                build_list_files=build_list_files,
                jamfile=jamfile,
                jamline=lnnum))

        elif entry[0] == 'run':
            build_list_files = get_tokens_from_section(0, entry[1:])
            arg_list_files = get_tokens_from_section(2, entry[1:])

            builds.append(BuildItem(
                short_name=build_name,
                build_list_files=build_list_files,
                jamfile=jamfile,
                jamline=lnnum))

            tests.append(BoostPythonTest_Run(
                short_name=test_name,
                arg_list_files=arg_list_files,
                depends=[build_name],
                jamfile=jamfile,
                jamline=lnnum))

        elif entry[0] == 'run':
            build_list_files = get_tokens_from_section(0, entry[1:])
            arg_list_files = get_tokens_from_section(2, entry[1:])

            builds.append(BuildItem(
                short_name=build_name,
                build_list_files=build_list_files,
                jamfile=jamfile,
                jamline=lnnum))

            tests.append(BoostPythonTest_Run(
                short_name=test_name,
                arg_list_files=arg_list_files,
                depends=[build_name],
                jamfile=jamfile,
                jamline=lnnum))

        elif entry[0] == 'bpl-test':
            section0 = get_tokens_from_section(0, entry[1:])
            if (len(section0)) != 1:
                raise GenException("Failed to parse '{}' - stopped at line {}".format(jamfile, lnnum))

            bpl_id = section0[0]
            depends = get_tokens_from_section(1, entry[1:])
            raise GenException("Failed to parse '{}' - TODO")


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
