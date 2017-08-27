#!/usr/bin/env python3

#
# File:   generate.py
# Authors:
#   Brendan Annable <brendan.annable@uon.edu.au>
#   Jake Woods <jake.f.woods@gmail.com>
#   Trent Houliston <trent@houliston.me>
#
import sys
import re
import os
import textwrap
import itertools
from banner import ampscii
from banner import bigtext

role_name = sys.argv[1]
banner_file = sys.argv[2]
module_path = sys.argv[3]
role_modules = sys.argv[4:]

# Open our output role file
with open(role_name, 'w') as file:

    # We use our NUClear header
    file.write('#include <nuclear>\n\n')

    # Add our module headers
    for module in role_modules:
        # Each module is given to us as Namespace::Namespace::Name.
        # we need to replace the ::'s with /'s so we can include them.

        # module::a::b::C
        # module/a/b/C/src/C.h

        # replace :: with /
        header = re.sub(r'::', r'/', module)
        # replace last name with src/name.h
        header = re.sub(r'([^\/]+)$', r'\1/src/\1.h', header)
        file.write('#include "{}"\n'.format(header))

    # Add our main function and include headers
    main = textwrap.dedent("""\
        int main(int argc, char** argv) {""")
    file.write(main)

    file.write('\n\n    // Print the logo generated by ampscii\n')

    # Generate our banner from our banner image
    banner = ampscii(banner_file)
    banner_lines = banner.replace('\x1b', '\\x1b').split('\n')[:-1]
    for l in banner_lines:
        file.write('    std::cerr << "{}" << std::endl;\n'.format(l))


    file.write('\n    // Print the name of the role in big letters\n')

    # Insert banner for the name of the executing role
    role_banner_lines = bigtext(os.path.splitext(os.path.basename(role_name))[0]).split('\n')[:-1]
    for l in role_banner_lines:
        file.write('    std::cerr << R"({})" << std::endl;\n'.format(l))


    start = """\

    NUClear::PowerPlant::Configuration config;
    unsigned int nThreads = std::thread::hardware_concurrency() + 2;
    config.thread_count = nThreads >= 4 ? nThreads : 4;

    NUClear::PowerPlant plant(config, argc, const_cast<const char**>(argv));"""

    file.write(start)

    for module in role_modules:
        file.write('    std::cerr << "Installing " << "{0}" << std::endl;\n'.format(module))
        file.write('    plant.install<module::{0}>();\n'.format(module))

    end = """
    plant.start();
    return 0;
}"""
    file.write(end)
    file.write('\n')
