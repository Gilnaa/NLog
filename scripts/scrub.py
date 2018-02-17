#!/usr/bin/env python

import subprocess
import re
import json
import time
import struct
import sys

__author__ = 'Gilad Naaman'

MAGIC = 0x676F4C4E

#   template<size_t N>
#   struct Entry
#   {
#       uint32_t magic;
#       uint32_t objectId;
#       uint16_t lineNumber;
#       uint16_t columnNumber;
#       uint32_t messageSize;
#       char msg[N];
#   } __attribute__((packed));
class Entry:
    def __init__(self, object_id, line_number, text):
        self.object_id = object_id
        self.line_number = line_number
        self.text = text

    @classmethod
    def parse(cls, section):
        STRUCT_STRING = "4I"
        HEADER_LENGTH = 16

        entries = []
        while len(section) > HEADER_LENGTH:
            header = section[:HEADER_LENGTH]
            section = section[HEADER_LENGTH:]

            magic, object_id, line_number, message_size = struct.unpack(STRUCT_STRING, header)

            if magic != MAGIC:
                raise ValueError("Invalid NLog magic")

            if len(section) < message_size:
                raise ValueError("Malformed section: not enough bytes for message")

            message = section[:message_size].strip('\x00')
            section = section[message_size:]

            entries.append(Entry(object_id, line_number, message))

            if len(section) > 0:
                try:
                    next_magic = section.index(struct.pack("I", MAGIC))
                    section = section[next_magic:]
                except:
                    break

        return entries

#   template<size_t N>
#   struct TranslationUnitMetadata
#   {
#       uint32_t magic;
#       uint32_t objectId;
#       uint32_t nameSize;
#       char name[N];
#   };
class TranslationUnitMetadata:
    def __init__(self, object_id, file_name):
        self.object_id = object_id
        self.file_name = file_name
        self.entries = []

    @classmethod
    def parse(cls, section):
        STRUCT_STRING = "III": {
        HEADER_LENGTH = 12

        objects = []
        while len(section) > HEADER_LENGTH:
            header = section[:HEADER_LENGTH]
            section = section[HEADER_LENGTH:]

            magic, object_id, name_size = struct.unpack(STRUCT_STRING, header)

            if magic != MAGIC:
                raise ValueError("Invalid NLog magic")

            if len(section) < name_size:
                raise ValueError("Malformed section: not enough bytes for message")

            name = section[:name_size].strip('\x00')
            section = section[name_size:]

            id_collisions = list(filter(lambda o: o.object_id == object_id, objects))
            if len(id_collisions) != 0:
                raise ValueError("Collision for ID %08x. Files: '%s', '%s'" % (object_id, id_collisions[0].file_name, name))

            objects.append(TranslationUnitMetadata(object_id, name))

            if len(section) > 0:
                try:
                    next_magic = section.index(struct.pack("I", MAGIC))
                    section = section[next_magic:]
                except:
                    break

        return objects


def get_section_data(source_file, objdump_line):
    index, name, size, vma, lma, offset, alignment = objdump_line.strip().split()

    source_file.seek(int(offset, 16))
    return source_file.read(int(size, 16))


def main():
    source_file_name = sys.argv[1]

    dump = subprocess.check_output(['objdump', '-h', source_file_name]).split('\n')
    nlog_objects = filter(lambda line: re.search('.nlog_objects', line), dump)[0]
    nlog_entries = filter(lambda line: re.search('.nlog_entries', line), dump)[0]
    with open(source_file_name, 'r') as source_file:
        nlog_entries = Entry.parse(get_section_data(source_file, nlog_entries))
        nlog_objects = TranslationUnitMetadata.parse(get_section_data(source_file, nlog_objects))

    for o in nlog_objects:
        entries = filter(lambda e: e.object_id == o.object_id, nlog_entries)
        o.entries.extend(entries)

    # print 'Objects:'
    # for o in nlog_objects:
    #     print "\t%08x -> %s" % (o.object_id, o.file_name)
    #
    # print 'Entries:'
    # for e in nlog_entries:
    #     print "\t%08x:%u -> %s" % (e.object_id, e.line_number, e.text)



    output_file = {
        'source_file': source_file_name,
        'timestamp': time.ctime(),
        'objects': [{'id': o.object_id, 'name': o.file_name, 'entries': {e.line_number: e.text for e in o.entries}} for o in nlog_objects],
    }

    print json.dumps(output_file, indent=4)


if __name__ == '__main__':
    main()