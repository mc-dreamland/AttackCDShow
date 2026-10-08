# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import os
import re
from datetime import datetime
from glob import glob
from zipfile import ZipFile, ZIP_DEFLATED

counter = 0


def get_now(fmt="%Y.%m.%d-%H%M%S"):
    return datetime.now().strftime(fmt)


def get_year_tuple():
    now = datetime.now().timetuple()
    return (now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0)


def print_counter(message=""):
    global counter
    counter += 1
    print("{}:{}".format(counter, message).decode("utf8"), end='\r')


def any_match(text, regular_expressions):
    for r in regular_expressions:
        if re.match(r, text):
            return True
    return False


def remove_import(full_path):
    content = open(full_path, "r").read()
    contents = content.splitlines(True)
    result = []
    find_import = False
    start_index = 0
    end_index = 0
    for index, line in enumerate(contents):
        if find_import:
            if line.startswith("    from ") or line.startswith("    import "):
                continue
            else:
                end_index = index
                break
        if line.strip() == "if False:":
            find_import = True
            start_index = index
    if 0 < start_index < end_index:
        result.extend(contents[:start_index])
        result.extend(contents[end_index:])
        return "".join(result)
    return content


def dir_zip(input_dir, zip_open, regular_expressions, extra_exclude):
    # type: (str, ZipFile, list[str]) -> None
    def search(path, z_F):
        # type: (str, ZipFile) -> None
        for f in os.listdir(path):
            if f in extra_exclude:
                continue
            if any_match(f, regular_expressions):
                continue
            ful_path = os.path.join(path, f)
            if os.path.isdir(ful_path):
                print_counter(f)
                z_F.write(ful_path)
                if not os.listdir(ful_path):
                    pass
                else:
                    search(ful_path, z_F)
            else:
                print_counter(f)
                if f.endswith(".py"):
                    modified_content = remove_import(ful_path)
                    z_F.writestr(ful_path, modified_content)
                else:
                    z_F.write(ful_path)

    print_counter(input_dir)
    zip_open.write(input_dir)
    search(input_dir, zip_open)


if __name__ == "__main__":

    exclude = {
        'editor.name', 'studio.json'
    }

    user_regexs = []
    LOCALAPPDATA = os.getenv("LOCALAPPDATA")
    if LOCALAPPDATA:
        config = os.path.join(os.getenv("LOCALAPPDATA"), 'Netease/MCStudio/config/app/app.conf')
        if os.path.exists(config):
            data = json.load(open(config))
            for regex in data['ExcludeRegexs']:
                user_regexs.append(regex['Pattern'].replace('\\\\', '\\'))

    work_space = os.getcwd()
    _, name = os.path.split(work_space)

    output_file = 'Cpp_AddOn_{}_{}.zip'.format(name, get_now())
    index = 0
    while os.path.exists(output_file):
        index += 1
        output_file = 'Cpp_AddOn_{}_{}_{}.zip'.format(name, get_now(), index)

    print("正在将打包: {} 为 {}".format(work_space, output_file).decode("utf8"))

    z = ZipFile(output_file, 'w', ZIP_DEFLATED)
    packs = glob('*/*manifest.json')
    packed = set()
    for pack in packs:
        pack_dir, _ = os.path.split(pack)
        if pack_dir not in packed:
            print_counter()
            os.chdir(work_space)
            dir_zip(pack_dir, z, user_regexs, exclude)
            packed.add(pack_dir)
    z.comment = 'zipped by heypixel, using python'
    time_tuple = get_year_tuple()
    for k in z.infolist():
        k.date_time = time_tuple
    z.close()
    print("")
    print("打包完成，按回车键退出".decode("utf8"))
    raw_input()
