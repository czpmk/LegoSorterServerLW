# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: LegoAnalysis.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import Messages_pb2 as Messages__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12LegoAnalysis.proto\x12\x08\x61nalysis\x1a\x0eMessages.proto2\x9f\x01\n\x0cLegoAnalysis\x12\x41\n\x0c\x44\x65tectBricks\x12\x14.common.ImageRequest\x1a\x1b.common.ListOfBoundingBoxes\x12L\n\x17\x44\x65tectAndClassifyBricks\x12\x14.common.ImageRequest\x1a\x1b.common.ListOfBoundingBoxesB)\n\x14\x63om.lsorter.analysisB\x11LegoAnalysisProtob\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'LegoAnalysis_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\024com.lsorter.analysisB\021LegoAnalysisProto'
  _LEGOANALYSIS._serialized_start=49
  _LEGOANALYSIS._serialized_end=208
# @@protoc_insertion_point(module_scope)
