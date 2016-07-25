#!/usr/bin/env python
import argparse
import xml.etree.ElementTree as ET
import re

def groups(iterable, count=2, fill=None):
    """
    generator which returns tuples of items from a list
    by groups of COUNT (default: 2) items
    """
    if count < 1:
        raise ValueError
    temp = list()
    for element in iterable:
        temp.append(element)
        if len(temp) == count:
            yield tuple(temp)
            temp = list()
    if len(temp) and fill is not None:
        yield temp.extend([fill for fill in range(count - len(temp))])

def get_components(item):
    """
    extract color components from the base color
    """
    result = {}
    for key, value in groups(item):
        match = re.match('(Red|Green|Blue) Component', key.text)
        if match:
            result[match.group(1).lower()] = int(float(value.text) * 255)
    return [result[x] for x in ('red', 'green', 'blue')]

def get_ansi_colors(items):
    """
    extracts the colors from the xml items
    """
    results = {}
    for key, value in groups(items):
        match = re.match('^Ansi (\d+) Color$', key.text)
        if match:
            results[int(match.group(1))] = get_components(value)
    return [results[i] for i in range(len(results))]

def print_kernel_vt_params(ansi_colors):
    """
    prints kernel command-line params for vt colors
    """
    colors = [x for x in zip(*ansi_colors)]
    names = ['red', 'grn', 'blu']
    print(' '.join(['vt.default_{}={}'
                    .format(name, ','.join(['0x{:x}'.format(i)
                                            for i in values]))
                    for (name, values) in zip(names, colors)]))

def main(arguments=None):

    parser = argparse.ArgumentParser()
    parser.add_argument('itermcolorsfile', type=argparse.FileType('r'),
                        help='iterm color file to open')
    args = parser.parse_args()

    root = ET.fromstring(args.itermcolorsfile.read())
    print_kernel_vt_params(get_ansi_colors(root.findall('./dict/')))

if __name__ == '__main__':
    main()
