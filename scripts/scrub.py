#!/usr/bin/env python

import subprocess
import re
import json
import argparse
import time

import sys

__author__ = 'Gilad Naaman'
__all__ = ['scrub_object_file']

NLOG_MESSAGE_PATTERN = '*nlog-msg*'


class NLogContext(object):
    def __init__(self, source_file, output=None):
        self.source_file = source_file
        self.output = output
        self.messages = None
        self.timestamp = time.ctime()

    @staticmethod
    def parse_section_data(name, offset, size):
        match = re.match('.nlog-msg-(?P<objectID>0x[0-9a-f]+)-(?P<messageID>[0-9]+)', name, re.IGNORECASE)
        object_id = int(match.group('objectID'), 16)
        message_id = int(match.group('messageID'))
        offset = int(offset, 16)
        size = int(size, 16)
        return object_id, message_id, offset, size

    def get_nlog_sections(self):
        dump = subprocess.check_output(['objdump', '-h', self.source_file]).split('\n')
        data = filter(lambda line: re.search(".*nlog-msg.*", line), dump)

        object_file = open(self.source_file, 'r')
        messages = []

        for line in data:
            # Parse line
            index, name, size, vma, lma, offset, alignment = line.strip().split()

            # Extract and parse metadata
            object_id, message_id, offset, size = self.parse_section_data(name, offset, size)

            # Read message data
            object_file.seek(offset)
            string = object_file.read(size).strip('\x00')
            messages.append((object_id, message_id, string))

        object_file.close()

        return messages

    def scrub(self):
        assert self.messages is None

        self.messages = {}
        data = self.get_nlog_sections()

        for object_id, message_id, string in data:
            if object_id not in self.messages:
                self.messages[object_id] = {}

            if message_id in self.messages[object_id]:
                raise ValueError('Duplicated ID pairings: %08x, %08x', object_id, message_id)

            self.messages[object_id][message_id] = string

        return self.messages

    def serialize(self):
        if self.output is None:
            return

        if self.messages is None:
            self.scrub()

        whole_file = {
            'source_file': args.object_file_path,
            'timestamp': time.ctime(),
            'messages': self.messages
        }

        json.dump(whole_file, self.output)

    def count(self):
        if self.messages is None:
            self.scrub()

        cnt = 0
        for object_id, messages in self.messages.items():
            cnt += len(messages)

        return cnt

    def clean(self):
        subprocess.call(['objcopy', '--remove-section', NLOG_MESSAGE_PATTERN, self.source_file])


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='Searches an ELF file for NLog messages, collects them, and strips them off of the ELF file.')
    arg_parser.add_argument('object_file_path',
                            help='The path to the input object file.')
    arg_parser.add_argument('nlog_dictionary_path', nargs='?',
                            help='The name of the resulting dictionary file.')
    group = arg_parser.add_mutually_exclusive_group()

    group.add_argument('-c', '--clean', action='store_true',
                            help='Do not extract messages, just strip the ELF.')
    group.add_argument('-d', '--dirty', action='store_true',
                            help='Keep the log messages in the ELF after extraction.')

    arg_parser.add_argument('--count', action='store_true',
                            help='Count NLog messages in an ELF file.')
    arg_parser.add_argument('-t', '--trim', action='store_true',
                            help='Do not write to output if the ELF does not contain any messages.')

    args = arg_parser.parse_args()

    context = NLogContext(args.object_file_path)

    if args.count or args.clean:
        context.output = None
    elif args.nlog_dictionary_path is not None:
        context.output = open(args.nlog_dictionary_path, 'w+')
    elif not args.clean and not args.count:
        context.output = sys.stdout

    if args.count:
        print context.count()

    if args.clean:
        context.clean()

    if not args.trim or context.count() > 0:
        context.serialize()

    if not args.dirty:
        context.clean()

    if context.output is not None:
        context.output.close()
