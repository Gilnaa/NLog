#!/usr/bin/env python

import json
import argparse


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='Searches a NLog dictionary for the given indicies')

    arg_parser.add_argument('nlog_dictionary_path', help='The name of the resulting dictionary file.')
    arg_parser.add_argument('message_id')

    args = arg_parser.parse_args()

    message_id = str(int(args.message_id, 0))

    with open(args.nlog_dictionary_path, 'r') as dictionary:
        data = json.load(dictionary)

    if 'messages' not in data or len(data['messages']) == 0:
        print 'Malformed or empty dictionary.'
        exit(1)

    logs = data['messages']
    if message_id not in logs:
        print 'Message ID (%#08x) not found in the dictionary' % message_id
        exit(1)

    print logs[message_id]
