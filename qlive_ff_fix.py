#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim:set softtabstop=4 | set expandtab | set tabstop=4
#
# Description:
# -----------
# Even if I think that the new versioning system of Firefox sucks,
# Firefox is still my prefered web browser.
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


from optparse import OptionParser
import zipfile
import libxml2
import os.path
import shutil

_FF_VERSION='7'

def replace_xml_xml(xml_data, version):
    """
    http://mikekneller.com/kb/python/libxml2python/part1
    """
    doc = libxml2.parseDoc(xml_data)
    root = doc.children
    #iterate over children of verse
    child1 = root.children
    while child1 is not None:
        child2 = child1.children
        while child2 is not None:
            child3 = child2.children
            while child3 is not None:
                child4 = child3.children
                while child4 is not None:
                    if child4.name == 'maxVersion':
                        child4.setContent(version)
                        return doc.serialize()
                    child4 = child4.next
                child3 = child3.next
            child2 = child2.next
        child1 = child1.next
    doc.freeDoc()

def parse_options(default_firefox_version):
    """
    Reads the arguments given by the user
    """
    parser = OptionParser("usage: %prog [options] QuakeLivePlugin_xyz.xpi", version="%prog 1.0")
    parser.add_option("-o", "--overwrite", action="store_true", dest="overwrite",
                    help="Overwrite current file instead of creating a new file")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                    help="Verbose mode")
    parser.add_option("-V", "--ff_version", default=default_firefox_version,
                    help="Your Firefox version [default: %default]")
    (options, args) = parser.parse_args()

    # do some checks
    if len(args) < 1:
         parser.error("Please write the plugin file file.")

    return (options, args[0])

if __name__ == "__main__":

    (options, xpi_filename) = parse_options(default_firefox_version=_FF_VERSION)

    # Open the file read only, fetch the install.rdf and close the file
    try:
        xpi_file = zipfile.ZipFile(xpi_filename, "r")
    except zipfile.BadZipfile:
        print "it looks like %s is not a zip file" % filename
        exit(1)

    install_rdf = xpi_file.read("install.rdf")


    # Create a new xml file
    new_rdf_xml = replace_xml_xml(install_rdf, options.ff_version + '.*')

    # Determine the new xpi filename
    basename, extension = os.path.splitext(xpi_filename)
    new_xpi_filename = basename + "-fixed" + extension

    # Create the new xpi file
    new_xpi_file = zipfile.ZipFile(new_xpi_filename, "w")

    for item in xpi_file.infolist():
        zipped_file = xpi_file.read(item.filename)
        if (item.filename != 'install.rdf'):
            new_xpi_file.writestr(item, zipped_file)

    # Write the xml data into a temporary location
    temp_install_rdf_filename = "/tmp/install.rdf"
    f = open(temp_install_rdf_filename, "w")
    f.write(new_rdf_xml)
    f.close()

    # add temp install.rdf to new xpi file
    new_xpi_file.write(temp_install_rdf_filename, 'install.rdf')
    # temp install.rdf is now useless
    os.unlink(temp_install_rdf_filename)

    xpi_file.close()
    new_xpi_file.close()

    if options.overwrite:
        shutil.move(new_xpi_filename, xpi_filename)




