"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from json import load
from os.path import join, dirname
from os import listdir
from argparse import ArgumentParser, ArgumentTypeError
from copy import deepcopy
from tools.targets import TARGET_NAMES, Target, update_target_data
from tools.toolchains import TOOLCHAINS, TOOLCHAIN_CLASSES
from tools.utils import argparse_force_uppercase_type, \
    argparse_lowercase_hyphen_type, argparse_many, \
    argparse_filestring_type, args_error, argparse_profile_filestring_type,\
    argparse_deprecate
from tools.app_layout import regions_to_common_pairs
from tools.app_layout import region_to_ld_pairs
from tools.app_layout import layout_to_regions
from tools.app_layout import regions_with_entry
from tools.arm_pack_manager import Cache
from tools.targets import TARGET_MAP

FLAGS_DEPRECATION_MESSAGE = "Please use the --profile argument instead.\n"\
                            "Documentation may be found in "\
                            "docs/Toolchain_Profiles.md"

def get_default_options_parser(add_clean=True, add_options=True,
                               add_app_config=False):
    """Create a new options parser with the default compiler options added

    Keyword arguments:
    add_clean - add the clean argument?
    add_options - add the options argument?
    """
    parser = ArgumentParser()

    targetnames = TARGET_NAMES
    targetnames.sort()
    toolchainlist = list(TOOLCHAINS)
    toolchainlist.sort()

    parser.add_argument("-m", "--mcu",
                        help=("build for the given MCU (%s)" %
                              ', '.join(targetnames)),
                        metavar="MCU")

    parser.add_argument("-t", "--tool",
                        help=("build using the given TOOLCHAIN (%s)" %
                              ', '.join(toolchainlist)),
                        metavar="TOOLCHAIN",
                        type=argparse_many(
                            argparse_force_uppercase_type(
                                toolchainlist, "toolchain")))

    parser.add_argument("--color",
                        help="print Warnings, and Errors in color",
                        action="store_true", default=False)

    parser.add_argument("--cflags",
                        type=argparse_deprecate(FLAGS_DEPRECATION_MESSAGE),
                        help="Deprecated. " + FLAGS_DEPRECATION_MESSAGE)

    parser.add_argument("--asmflags",
                        type=argparse_deprecate(FLAGS_DEPRECATION_MESSAGE),
                        help="Deprecated. " + FLAGS_DEPRECATION_MESSAGE)

    parser.add_argument("--ldflags",
                        type=argparse_deprecate(FLAGS_DEPRECATION_MESSAGE),
                        help="Deprecated. " + FLAGS_DEPRECATION_MESSAGE)

    if add_clean:
        parser.add_argument("-c", "--clean", action="store_true", default=False,
                            help="clean the build directory")

    if add_options:
        parser.add_argument("--profile", dest="profile", action="append",
                            type=argparse_profile_filestring_type,
                            help="Build profile to use. Can be either path to json" \
                            "file or one of the default one ({})".format(", ".join(list_profiles())),
                            default=[])
    if add_app_config:
        parser.add_argument("--app-config", default=None, dest="app_config",
                            type=argparse_filestring_type,
                            help="Path of an app configuration file (Default is to look for 'mbed_app.json')")

    return parser

def list_profiles():
    """Lists available build profiles

    Checks default profile directory (mbed-os/tools/profiles/) for all the json files and return list of names only
    """
    return [fn.replace(".json", "") for fn in listdir(join(dirname(__file__), "profiles")) if fn.endswith(".json")]

def extract_profile(parser, options, toolchain, fallback="develop"):
    """Extract a Toolchain profile from parsed options

    Positional arguments:
    parser - parser used to parse the command line arguments
    options - The parsed command line arguments
    toolchain - the toolchain that the profile should be extracted for
    """
    profiles = []
    filenames = options.profile or [join(dirname(__file__), "profiles",
                                         fallback + ".json")]
    for filename in filenames:
        contents = load(open(filename))
        if toolchain not in contents:
            args_error(parser, ("argument --profile: toolchain {} is not"
                                " supported by profile {}").format(toolchain,
                                                                   filename))
        profiles.append(contents)

    return profiles

def mcu_is_enabled(parser, mcu):
    if "Cortex-A" in TARGET_MAP[mcu].core:
        args_error(
            parser,
            ("%s Will be supported in mbed OS 5.6. "
             "To use the %s, please checkout the mbed OS 5.4 release branch. "
             "See https://developer.mbed.org/platforms/Renesas-GR-PEACH/#important-notice "
             "for more information") % (mcu, mcu))
    return True
    
def extract_mcus(parser, options):
    try:
        if options.source_dir:
            for source_dir in options.source_dir:
                Target.add_extra_targets(source_dir)
            update_target_data()
    except KeyError:
        pass
    targetnames = TARGET_NAMES
    targetnames.sort()
    try:
        return argparse_many(argparse_force_uppercase_type(targetnames, "MCU"))(options.mcu)
    except ArgumentTypeError as exc:
        args_error(parser, "argument -m/--mcu: {}".format(str(exc)))


def extract_layouts(options, toolchain, target, layout, artifact_name, base_profile):
    """Extract a target layout from parsed options for each configuration

    Positional arguments:
    parser - parser used to parse the command line arguments
    options - The parsed command line arguments
    toolchain - the toolchain that the profile should be extracted for
    target - target to extract the layout for
    """
    tc_class = TOOLCHAIN_CLASSES[toolchain]
    common_flags = []
    rom_start, rom_size = _get_target_rom_start_size(target)
    regions = list(layout_to_regions(open(layout, "r"), rom_start, rom_size))
    for name, val in regions_to_common_pairs(regions):
        common_flags.append("-D%s=0x%x" % (name, val))
    common_flags.append("-DCUSTOM_ENTRY_POINT")

    for region in regions_with_entry(regions):
        linker_flags = []
        for name, val in region_to_ld_pairs(region, rom_start):
            linker_flags.append(tc_class.make_ld_define(name, val))

        redirect_arg = tc_class.redirect_main(region.name, options.build_dir)
        if redirect_arg:
            linker_flags.append(redirect_arg)

        profile_entry = {toolchain: {'c': [], 'cxx': [],
                                     'common': common_flags,
                                     'asm': [], 'ld': linker_flags}}
        new_profile = deepcopy(base_profile)
        new_profile.append(profile_entry)
        yield (artifact_name + "_" + region.name, region.addr, new_profile)

def _get_target_rom_start_size(name):
    """Return start and size of first rom region of the target"""
    cache = Cache(True, False)
    device_name = TARGET_MAP[name].device_name #TODO - handle no device name
    target_info = cache.index[device_name]

    roms = [(_str_to_int(info["start"]), _str_to_int(info["size"]))
            for mem, info in target_info["memory"].items() if "ROM" in mem]
    roms.sort(key=lambda entry:entry[0])
    return roms[0]

def _str_to_int(val_str):
    return int(val_str[2:], 16) if val_str[0:2] == "0x" else int(val_str)
