#!/usr/bin/env python

import argparse
import os
import os.path
import zipfile


def make_module_catalog(src, catalog, is_root):
    root_path = os.path.abspath(os.path.normpath(src))
    if is_root:
        root_arcname = ''
    else:
        root_arcname = os.path.basename(root_path)
    if not os.path.isdir(root_path):
        mt = os.path.getmtime(root_path)
        catalog.append((root_path, root_arcname, mt))
        return
    subdirs = [(root_path, root_arcname)]
    while subdirs:
        idx = len(subdirs) - 1
        subdir_path, subdir_archname = subdirs[idx]
        del subdirs[idx]
        for item in sorted(os.listdir(subdir_path)):
            if item in ['__pycache__'] or item.endswith('.pyc'):
                continue
            item_path = os.path.join(subdir_path, item)
            if subdir_archname:
                item_arcname = '/'.join([subdir_archname, item])
            else:
                item_arcname = item
            if os.path.isdir(item_path):
                subdirs.append((item_path, item_arcname))
            else:
                mt = os.path.getmtime(item_path)
                catalog.append((item_path, item_arcname, mt))


def zip_rebuild_required(zipfilename, catalog):
    if not os.path.exists(zipfilename):
        return True
    zip_mtime = os.path.getmtime(zipfilename)
    if zip_mtime < os.path.getmtime(__file__):
        return True
    for entry in catalog:
        mt = entry[2]
        if zip_mtime < mt:
            return True
    return False


def mk_pyzip(sources, roots, outzip):
    zipfilename = os.path.abspath(os.path.normpath(outzip))
    display_zipname = os.path.basename(zipfilename)
    dir_of_zip = os.path.dirname(zipfilename)
    if not os.path.exists(dir_of_zip):
        os.makedirs(dir_of_zip)

    catalog = []

    if roots is not None:
        for src in roots:
            make_module_catalog(src, catalog, is_root=True)

    if sources is not None:
        for src in sources:
            make_module_catalog(src, catalog, is_root=False)

    if not zip_rebuild_required(zipfilename, catalog):
        print("::: python zip package '{}' is up-to-date.".format(zipfilename))
        return

    print("::: compiling python zip package '{}' ...".format(zipfilename))
    with zipfile.ZipFile(zipfilename, "w", zipfile.ZIP_DEFLATED) as fzip:
        for entry in catalog:
            fname, arcname = entry[0], entry[1]
            fzip.write(fname, arcname)
            print("::: {} >>> {}/{}".format(fname, display_zipname, arcname))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', nargs='*')
    parser.add_argument('--src-root', nargs='*')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    mk_pyzip(args.src, args.src_root, args.out)


if __name__ == '__main__':
    main()
