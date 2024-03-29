# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import Messages_pb2 as Messages__pb2


class LegoSorterStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.processNextImage = channel.unary_unary(
                '/sorter.LegoSorter/processNextImage',
                request_serializer=Messages__pb2.ImageRequest.SerializeToString,
                response_deserializer=Messages__pb2.ListOfBoundingBoxesWithIndexes.FromString,
                )
        self.getConfiguration = channel.unary_unary(
                '/sorter.LegoSorter/getConfiguration',
                request_serializer=Messages__pb2.Empty.SerializeToString,
                response_deserializer=Messages__pb2.SorterConfiguration.FromString,
                )
        self.updateConfiguration = channel.unary_unary(
                '/sorter.LegoSorter/updateConfiguration',
                request_serializer=Messages__pb2.SorterConfiguration.SerializeToString,
                response_deserializer=Messages__pb2.Empty.FromString,
                )
        self.startMachine = channel.unary_unary(
                '/sorter.LegoSorter/startMachine',
                request_serializer=Messages__pb2.Empty.SerializeToString,
                response_deserializer=Messages__pb2.Empty.FromString,
                )
        self.stopMachine = channel.unary_unary(
                '/sorter.LegoSorter/stopMachine',
                request_serializer=Messages__pb2.Empty.SerializeToString,
                response_deserializer=Messages__pb2.Empty.FromString,
                )


class LegoSorterServicer(object):
    """Missing associated documentation comment in .proto file."""

    def processNextImage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getConfiguration(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def updateConfiguration(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def startMachine(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def stopMachine(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_LegoSorterServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'processNextImage': grpc.unary_unary_rpc_method_handler(
                    servicer.processNextImage,
                    request_deserializer=Messages__pb2.ImageRequest.FromString,
                    response_serializer=Messages__pb2.ListOfBoundingBoxesWithIndexes.SerializeToString,
            ),
            'getConfiguration': grpc.unary_unary_rpc_method_handler(
                    servicer.getConfiguration,
                    request_deserializer=Messages__pb2.Empty.FromString,
                    response_serializer=Messages__pb2.SorterConfiguration.SerializeToString,
            ),
            'updateConfiguration': grpc.unary_unary_rpc_method_handler(
                    servicer.updateConfiguration,
                    request_deserializer=Messages__pb2.SorterConfiguration.FromString,
                    response_serializer=Messages__pb2.Empty.SerializeToString,
            ),
            'startMachine': grpc.unary_unary_rpc_method_handler(
                    servicer.startMachine,
                    request_deserializer=Messages__pb2.Empty.FromString,
                    response_serializer=Messages__pb2.Empty.SerializeToString,
            ),
            'stopMachine': grpc.unary_unary_rpc_method_handler(
                    servicer.stopMachine,
                    request_deserializer=Messages__pb2.Empty.FromString,
                    response_serializer=Messages__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'sorter.LegoSorter', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class LegoSorter(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def processNextImage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sorter.LegoSorter/processNextImage',
            Messages__pb2.ImageRequest.SerializeToString,
            Messages__pb2.ListOfBoundingBoxesWithIndexes.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def getConfiguration(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sorter.LegoSorter/getConfiguration',
            Messages__pb2.Empty.SerializeToString,
            Messages__pb2.SorterConfiguration.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def updateConfiguration(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sorter.LegoSorter/updateConfiguration',
            Messages__pb2.SorterConfiguration.SerializeToString,
            Messages__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def startMachine(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sorter.LegoSorter/startMachine',
            Messages__pb2.Empty.SerializeToString,
            Messages__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def stopMachine(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sorter.LegoSorter/stopMachine',
            Messages__pb2.Empty.SerializeToString,
            Messages__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
