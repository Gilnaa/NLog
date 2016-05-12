#!/usr/bin/env python

import argparse
import binascii
import os.path


def generate_object_id(data):
    return binascii.crc32(data) & 0xffffffff


def get_id_by_name(file_name):
    file_name = os.path.abspath(file_name)
    return generate_object_id(file_name)


def get_id_by_content(file_name):
    with open(file_name, 'r') as source_file:
        data = source_file.read()

    return generate_object_id(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates and prints an NLog ID for a source file.')
    parser.add_argument('source_file', help='The source file to generate an ID for.')
    parser.add_argument('-t', '--type', choices=['name', 'content'], default='name',
                        help="Specifies how to generate the ID, by the file's name or by its content.")
    parser.add_argument('--exit-status', action='store_true',
                        help="Return the ID as the program's exit status instead of printing it.")

    args = parser.parse_args()

    object_id = 0
    if args.type == 'name':
        object_id = get_id_by_name(args.source_file)
    elif args.type == 'content':
        object_id = get_id_by_content(args.source_file)

    if args.exit_status:
        exit(object_id)
    else:
        print format(object_id, 'x'),
