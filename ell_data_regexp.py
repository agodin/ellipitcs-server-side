#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import binascii
import struct
import re
import os
import json
from datetime import datetime

import eblob

sys.path.insert(0, "/usr/lib")
from libelliptics_python import *


meta_types = {
    1: "object",
    2: "groups",
    3: "check status",
    4: "namespace",
    5: "update",
    6: "checksum",
}

META_BLOB = re.compile('^data-1.\d+$')

def parse_meta(meta):
    meta_res = {}

    while len(meta):
        (header_type, header_length) = struct.unpack('<LL', meta[0:8])

        meta = meta[32:]
        if header_type == 1:
            meta_res[meta_types[header_type]] = meta[0:header_length]

        if header_type == 2:
            groups_fmt = '<' + 'L'*(header_length/4)
            meta_res[meta_types[header_type]] = struct.unpack(
                groups_fmt,
                meta[0:header_length]
            )

        if header_type == 5:
            update_fmt = '<' + 'QQQ'
            (flags, sec, nsec) = struct.unpack(
                update_fmt,
                meta[8:struct.calcsize(update_fmt)+8]
            )
            meta_res[meta_types[header_type]] = {
                'flags': flags,
                'date': datetime.fromtimestamp(sec).isoformat(' '),
                'nsec': nsec
            }
        meta = meta[header_length:]

    return meta_res


try:
    blob_dir
except NameError:
    blob_dir = os.path.dirname(os.path.abspath(os.curdir))


def process_blob(blob_dir, matcher):
    data = []

    blob = eblob.blob(blob_dir, data_mode='rb', index_mode='rb')

    for id in blob.iterate(want_removed=False):
        blob.read_data()
        meta = parse_meta(blob.data)
        if matcher.match(meta["object"]):
            data.append(meta)

    return data

def main(pattern):
    data = []
    matcher = re.compile(pattern)
    for f in os.listdir(blob_dir):
        if META_BLOB.match(f):
            data.extend(process_blob(os.path.join(blob_dir, f), matcher))
    return json.dumps(data)

try:
    pattern = str(__input_binary_data_tuple[0])
except NameError:
    pattern="^.*"

if len(pattern):
    __return_data = main(pattern)

print __return_data
