# Copyright 2014 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import os

from catkin_tools.argument_parsing import add_cmake_and_make_and_catkin_make_args
from catkin_tools.argument_parsing import add_context_args

from catkin_tools.context import Context


def prepare_arguments(parser):

    parser.description = "This verb is used to configure a catkin workspace's\
    configuration and layout. Calling `catkin config` with no arguments will\
    display the current config and affect no changes if a config already exists\
    for the current workspace and profile."

    # Workspace / profile args
    add_context_args(parser)

    context_group = parser.add_argument_group('Workspace Context', 'Options affecting the context of the workspace.')
    add = context_group.add_argument
    add('--init', action='store_true', default=False,
        help='Initialize a workspace if it does not yet exist.')
    add = context_group.add_mutually_exclusive_group().add_argument
    add('--extend', '-e', dest='extend_path', type=str,
        help='Explicitly extend the result-space of another catkin workspace, '
        'overriding the value of $CMAKE_PREFIX_PATH.')
    add('--no-extend', dest='extend_path', action='store_const', const='',
        help='Un-set the explicit extension of another workspace as set by --extend.')
    add = context_group.add_argument
    add('--mkdirs', action='store_true', default=False,
        help='Create directories required by the configuration (e.g. source space) if they do not already exist.')

    spaces_group = parser.add_argument_group('Spaces', 'Location of parts of the catkin workspace.')
    add = spaces_group.add_mutually_exclusive_group().add_argument
    add('-s', '--source-space', default=None,
        help='The path to the source space.')
    add('--default-source-space',
        action='store_const', dest='source_space', default=None, const=Context.DEFAULT_SOURCE_SPACE,
        help='Use the default path to the source space ("src")')
    add = spaces_group.add_mutually_exclusive_group().add_argument
    add('-b', '--build-space', default=None,
        help='The path to the build space.')
    add('--default-build-space',
        action='store_const', dest='build_space', default=None, const=Context.DEFAULT_BUILD_SPACE,
        help='Use the default path to the build space ("build")')
    add = spaces_group.add_mutually_exclusive_group().add_argument
    add('-d', '--devel-space', default=None,
        help='Sets the target devel space')
    add('--default-devel-space',
        action='store_const', dest='devel_space', default=None, const=Context.DEFAULT_DEVEL_SPACE,
        help='Sets the default target devel space ("devel")')
    add = spaces_group.add_mutually_exclusive_group().add_argument
    add('-i', '--install-space', default=None,
        help='Sets the target install space')
    add('--default-install-space',
        action='store_const', dest='install_space', default=None, const=Context.DEFAULT_INSTALL_SPACE,
        help='Sets the default target install space ("install")')
    add = spaces_group.add_argument
    add('-x', '--space-suffix',
        help='Suffix for build, devel, and install space if they are not otherwise explicitly set.')

    devel_group = parser.add_argument_group(
        'Devel Space', 'Options for configuring the structure of the devel space.')
    add = devel_group.add_mutually_exclusive_group().add_argument
    add('--isolate-devel', action='store_true', default=None,
        help='Build products from each catkin package into isolated devel spaces.')
    add('--merge-devel', dest='isolate_devel', action='store_false', default=None,
        help='Build products from each catkin package into a single merged devel spaces.')

    install_group = parser.add_argument_group(
        'Install Space', 'Options for configuring the structure of the install space.')
    add = install_group.add_mutually_exclusive_group().add_argument
    add('--install', action='store_true', default=None,
        help='Causes each package to be installed to the install space.')
    add('--no-install', dest='install', action='store_false', default=None,
        help='Disables installing each package into the install space.')

    add = install_group.add_mutually_exclusive_group().add_argument
    add('--isolate-install', action='store_true', default=None,
        help='Install each catkin package into a separate install space.')
    add('--merge-install', dest='isolate_install', action='store_false', default=None,
        help='Install each catkin package into a single merged install space.')

    build_group = parser.add_argument_group('Build Options', 'Options for configuring the way packages are built.')
    add_cmake_and_make_and_catkin_make_args(build_group)

    return parser


def main(opts):
    try:
        # Try to find a metadata directory to get context defaults
        # Otherwise use the specified directory
        context = Context.Load(opts.workspace, opts.profile, opts)

        if context.initialized() or opts.init:
            Context.Save(context)

        if opts.mkdirs and not context.source_space_exists():
            os.makedirs(context.source_space_abs)

        print(context.summary())

    except IOError as exc:
        # Usually happens if workspace is already underneath another catkin_tools workspace
        print('error: could not configure catkin workspace: %s' % exc.message)
        return 1

    return 0
