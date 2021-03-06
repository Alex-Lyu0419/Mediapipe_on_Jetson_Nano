# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import LivePlayer_pb2 as LivePlayer__pb2


class LivePlayerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.LiveStream = channel.unary_unary(
                '/LivePlayer/LiveStream',
                request_serializer=LivePlayer__pb2.Types.SerializeToString,
                response_deserializer=LivePlayer__pb2.Results.FromString,
                )


class LivePlayerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def LiveStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_LivePlayerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'LiveStream': grpc.unary_unary_rpc_method_handler(
                    servicer.LiveStream,
                    request_deserializer=LivePlayer__pb2.Types.FromString,
                    response_serializer=LivePlayer__pb2.Results.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'LivePlayer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class LivePlayer(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def LiveStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/LivePlayer/LiveStream',
            LivePlayer__pb2.Types.SerializeToString,
            LivePlayer__pb2.Results.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
