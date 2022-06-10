# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Messages.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='Messages.proto',
  package='common',
  syntax='proto3',
  serialized_options=b'\n\022com.lsorter.commonB\023CommonMessagesProto',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0eMessages.proto\x12\x06\x63ommon\"c\n\x0b\x42oundingBox\x12\x0c\n\x04ymin\x18\x01 \x01(\x05\x12\x0c\n\x04xmin\x18\x02 \x01(\x05\x12\x0c\n\x04ymax\x18\x03 \x01(\x05\x12\x0c\n\x04xmax\x18\x04 \x01(\x05\x12\r\n\x05label\x18\x05 \x01(\t\x12\r\n\x05score\x18\x06 \x01(\x02\":\n\x13ListOfBoundingBoxes\x12#\n\x06packet\x18\x01 \x03(\x0b\x32\x13.common.BoundingBox\"/\n\x0cImageRequest\x12\r\n\x05image\x18\x01 \x01(\x0c\x12\x10\n\x08rotation\x18\x02 \x01(\x05\"\x07\n\x05\x45mptyB)\n\x12\x63om.lsorter.commonB\x13\x43ommonMessagesProtob\x06proto3'
)




_BOUNDINGBOX = _descriptor.Descriptor(
  name='BoundingBox',
  full_name='common.BoundingBox',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='ymin', full_name='common.BoundingBox.ymin', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='xmin', full_name='common.BoundingBox.xmin', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ymax', full_name='common.BoundingBox.ymax', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='xmax', full_name='common.BoundingBox.xmax', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='label', full_name='common.BoundingBox.label', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='score', full_name='common.BoundingBox.score', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=26,
  serialized_end=125,
)


_LISTOFBOUNDINGBOXES = _descriptor.Descriptor(
  name='ListOfBoundingBoxes',
  full_name='common.ListOfBoundingBoxes',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='packet', full_name='common.ListOfBoundingBoxes.packet', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=127,
  serialized_end=185,
)


_IMAGEREQUEST = _descriptor.Descriptor(
  name='ImageRequest',
  full_name='common.ImageRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='image', full_name='common.ImageRequest.image', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='rotation', full_name='common.ImageRequest.rotation', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=187,
  serialized_end=234,
)


_EMPTY = _descriptor.Descriptor(
  name='Empty',
  full_name='common.Empty',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=236,
  serialized_end=243,
)

_LISTOFBOUNDINGBOXES.fields_by_name['packet'].message_type = _BOUNDINGBOX
DESCRIPTOR.message_types_by_name['BoundingBox'] = _BOUNDINGBOX
DESCRIPTOR.message_types_by_name['ListOfBoundingBoxes'] = _LISTOFBOUNDINGBOXES
DESCRIPTOR.message_types_by_name['ImageRequest'] = _IMAGEREQUEST
DESCRIPTOR.message_types_by_name['Empty'] = _EMPTY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

BoundingBox = _reflection.GeneratedProtocolMessageType('BoundingBox', (_message.Message,), {
  'DESCRIPTOR' : _BOUNDINGBOX,
  '__module__' : 'Messages_pb2'
  # @@protoc_insertion_point(class_scope:common.BoundingBox)
  })
_sym_db.RegisterMessage(BoundingBox)

ListOfBoundingBoxes = _reflection.GeneratedProtocolMessageType('ListOfBoundingBoxes', (_message.Message,), {
  'DESCRIPTOR' : _LISTOFBOUNDINGBOXES,
  '__module__' : 'Messages_pb2'
  # @@protoc_insertion_point(class_scope:common.ListOfBoundingBoxes)
  })
_sym_db.RegisterMessage(ListOfBoundingBoxes)

ImageRequest = _reflection.GeneratedProtocolMessageType('ImageRequest', (_message.Message,), {
  'DESCRIPTOR' : _IMAGEREQUEST,
  '__module__' : 'Messages_pb2'
  # @@protoc_insertion_point(class_scope:common.ImageRequest)
  })
_sym_db.RegisterMessage(ImageRequest)

Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), {
  'DESCRIPTOR' : _EMPTY,
  '__module__' : 'Messages_pb2'
  # @@protoc_insertion_point(class_scope:common.Empty)
  })
_sym_db.RegisterMessage(Empty)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
