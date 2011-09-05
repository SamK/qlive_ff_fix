#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim:set softtabstop=4 | set expandtab | set tabstop=4
#
# Description:
# -----------
# This script fixes the Quake Live plugin to match with your Firefox version.
#
# Usage:
# -----
# qlive_ff_fix.py --help
#
# Licence stuff:
# -------------
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details. */ 
#

__author__ = 'Samuel "samyboy" Krieg'
__credits__ = ["wolf1e"]
__license__ = "WTFPL"
__version__ = "1.1"

from optparse import OptionParser
from distutils.version import LooseVersion
import zipfile
import os.path
import shutil

"""
This is the default maxVersion if --ff_version is not set.
The wildcard is added automatically, no need to bother with ".*" stuff.
"""
_FF_MAX_VERSION='7'
"""The minimal version which requires the "unpack" line """
_UNPACK_VERSION='4'

def replace_xml_regexp(xml_data, ff_max_version):
    """
    1. Replace the maxversion value by "version" given in argument
        (The wildcard is added automatically)
    2. Adds the "unpack" element if needed

    This function uses regexp instead of libxml2
    """
    import re
    # This will be our new xml data (stored in an array)
    axml_data = []
    for line in xml_data.splitlines(True):
        """em:maxVersion found!"""
        if line.find("em:maxVersion") >= 0:
            line = re.sub(r'\d+(\.\d+)*(\.\*)?', ff_max_version, line)          
        axml_data.append(line)
        if line.find("em:creator") >= 0 and LooseVersion(ff_max_version) >= LooseVersion(_UNPACK_VERSION):
            """ Firefox versions upper than 4 need the unpack element """
            axml_data.append('    <em:unpack>true</em:unpack>\n')
    return ''.join(axml_data)

def replace_xml_libxml2(xml_data, ff_max_version):
    import libxml2
    """
    1. Replace the maxversion value by "version" given in argument
        (The wildcard is added automatically)
    2. Adds the "unpack" element if needed
    http://mikekneller.com/kb/python/libxml2python/part1

    This function uses libxml2 instead of regexp
    """
    doc = libxml2.parseDoc(xml_data)
    root = doc.children
    child1 = root.children
    # Is there a better way besides all those loops?
    # TODO: Find a better nicer way
    while child1 is not None:
        if child1.name  == 'Description' and LooseVersion(ff_max_version) >= LooseVersion(_UNPACK_VERSION):
            """ Firefox versions upper than 4 need the "unpack" element """
            # add new value here
            unpackNode = libxml2.newNode('em:unpack')
            unpackNode.setContent('true')
            child1.addChild(unpackNode)
        child2 = child1.children
        while child2 is not None:
            child3 = child2.children
            while child3 is not None:
                child4 = child3.children
                while child4 is not None:
                    if child4.name == 'maxVersion':
                        """em:maxVersion found!"""
                        child4.setContent(ff_max_version)
                    child4 = child4.next
                child3 = child3.next
            child2 = child2.next
        child1 = child1.next
    return doc.serialize()

def parse_options(default_firefox_version):
    """
    Reads the arguments given by the user
    """
    parser = OptionParser("usage: %prog [options] QuakeLivePlugin_xyz.xpi", version="%prog " + __version__)
    parser.add_option("-o", "--overwrite", action="store_true", dest="overwrite",
                    help="Overwrite the current file instead of creating a new file")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                    help="Verbose mode (not yet implemented)")
    parser.add_option("-V", "--ff_version", default=default_firefox_version,
                    help="Your Firefox version [default: %default]")
    parser.add_option("-r", "--regexp", "--wolf1e", action="store_true", dest="use_regexp",
                    help="Use regular expression provided by wolf1e instead of libxml2")
    (options, args) = parser.parse_args()

    # Argument checks
    if len(args) < 1:
         parser.error("Please specify a file. Use the '--help' argument for more informations.")

    return (options, args[0])

if __name__ == "__main__":
    """
    Main part
    """

    # retrieves the user options and the filename
    (options, xpi_filename) = parse_options(default_firefox_version=_FF_MAX_VERSION)

    # Open the file read only
    try:
        xpi_file = zipfile.ZipFile(xpi_filename, "r")
    except zipfile.BadZipfile:
        # FIXME: output errors to stderr
        print "The file '%s' does not looks like a proper xpi file" % xpi_filename
        exit(1)

    # read the install.rdf file
    install_rdf = xpi_file.read("install.rdf")
    # Create a new xml file
    if options.use_regexp:
        new_rdf_xml = replace_xml_regexp(install_rdf, options.ff_version + '.*')
    else:
        new_rdf_xml = replace_xml_libxml2(install_rdf, options.ff_version + '.*')

    # Determine the new xpi filename
    basename, extension = os.path.splitext(xpi_filename)
    new_xpi_filename = basename + "-fixed" + extension

    # Create the new xpi file
    new_xpi_file = zipfile.ZipFile(new_xpi_filename, "w")

    # populate the new xpi file with the old xpi file, exept install.rdf
    for item in xpi_file.infolist():
        zipped_file = xpi_file.read(item.filename)
        if (item.filename != 'install.rdf'):
            new_xpi_file.writestr(item, zipped_file)

    # Write the xml data into a temporary location
    # FIXME: use the tempfile module: http://docs.python.org/library/tempfile.html
    temp_install_rdf_filename = "/tmp/install.rdf"
    f = open(temp_install_rdf_filename, "w")
    f.write(new_rdf_xml)
    f.close()

    # add the new install.rdf to the new xpi file
    new_xpi_file.write(temp_install_rdf_filename, 'install.rdf')

    # temp install.rdf is now useless, time to delete
    os.unlink(temp_install_rdf_filename)

    # close both zip files
    xpi_file.close()
    new_xpi_file.close()

    # honor the "--overwrite" option
    if options.overwrite:
        shutil.move(new_xpi_filename, xpi_filename)


