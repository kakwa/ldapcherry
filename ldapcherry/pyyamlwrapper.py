# -*- coding: utf-8 -*-

import os
import sys
import yaml
from yaml.error import *
from yaml.nodes import *
from yaml.reader import *
from yaml.scanner import *
from yaml.parser import *
from yaml.composer import *
from yaml.constructor import *
from yaml.resolver import *


class RelationError(Exception):
    def __init__(self, key, value):
        self.key = key
        self.value = value


class DumplicatedKey(Exception):
    def __init__(self, host, key):
        self.host = host
        self.key = key


try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


# PyYaml wrapper that loads yaml files throwing an exception
# if a key is dumplicated
class MyLoader(Reader, Scanner, Parser, Composer, Constructor, Resolver):

    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        Constructor.__init__(self)
        Resolver.__init__(self)

    def construct_mapping(self, node, deep=False):
        exc = sys.exc_info()[1]
        if not isinstance(node, MappingNode):
            raise ConstructorError(
                None,
                None,
                "expected a mapping node, but found %s" % node.id,
                node.start_mark
                )
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "found unacceptable key (%s)" % exc, key_node.start_mark
                    )
            value = self.construct_object(value_node, deep=deep)
            if key in mapping:
                raise DumplicatedKey(key, '')
            mapping[key] = value
        return mapping


def loadNoDump(stream):
    loader = MyLoader(stream)
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
