# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: LegoAsyncSorter.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import Messages_pb2 as Messages__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15LegoAsyncSorter.proto\x12\x0b\x61syncSorter\x1a\x0eMessages.proto2\xa2\x02\n\x0fLegoAsyncSorter\x12\x33\n\x0cprocessImage\x12\x14.common.ImageRequest\x1a\r.common.Empty\x12\x44\n\x10getConfiguration\x12\r.common.Empty\x1a!.common.SorterConfigurationWithIP\x12G\n\x13updateConfiguration\x12!.common.SorterConfigurationWithIP\x1a\r.common.Empty\x12%\n\x05start\x12\r.common.Empty\x1a\r.common.Empty\x12$\n\x04stop\x12\r.common.Empty\x1a\r.common.EmptyB/\n\x17\x63om.lsorter.asyncSorterB\x14LegoAsyncSorterProtob\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'LegoAsyncSorter_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.lsorter.asyncSorterB\024LegoAsyncSorterProto'
  _LEGOASYNCSORTER._serialized_start=55
  _LEGOASYNCSORTER._serialized_end=345
# @@protoc_insertion_point(module_scope)
