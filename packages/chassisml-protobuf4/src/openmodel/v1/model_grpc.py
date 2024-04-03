# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: openmodel/v1/model.proto
# plugin: grpclib.plugin.main
import abc
import typing

import grpclib.const
import grpclib.client
if typing.TYPE_CHECKING:
    import grpclib.server

import openmodel.v1.model_pb2


class ModzyModelBase(abc.ABC):

    @abc.abstractmethod
    async def Status(self, stream: 'grpclib.server.Stream[openmodel.v1.model_pb2.StatusRequest, openmodel.v1.model_pb2.StatusResponse]') -> None:
        pass

    @abc.abstractmethod
    async def Run(self, stream: 'grpclib.server.Stream[openmodel.v1.model_pb2.RunRequest, openmodel.v1.model_pb2.RunResponse]') -> None:
        pass

    @abc.abstractmethod
    async def Shutdown(self, stream: 'grpclib.server.Stream[openmodel.v1.model_pb2.ShutdownRequest, openmodel.v1.model_pb2.ShutdownResponse]') -> None:
        pass

    def __mapping__(self) -> typing.Dict[str, grpclib.const.Handler]:
        return {
            '/ModzyModel/Status': grpclib.const.Handler(
                self.Status,
                grpclib.const.Cardinality.UNARY_UNARY,
                openmodel.v1.model_pb2.StatusRequest,
                openmodel.v1.model_pb2.StatusResponse,
            ),
            '/ModzyModel/Run': grpclib.const.Handler(
                self.Run,
                grpclib.const.Cardinality.UNARY_UNARY,
                openmodel.v1.model_pb2.RunRequest,
                openmodel.v1.model_pb2.RunResponse,
            ),
            '/ModzyModel/Shutdown': grpclib.const.Handler(
                self.Shutdown,
                grpclib.const.Cardinality.UNARY_UNARY,
                openmodel.v1.model_pb2.ShutdownRequest,
                openmodel.v1.model_pb2.ShutdownResponse,
            ),
        }


class ModzyModelStub:

    def __init__(self, channel: grpclib.client.Channel) -> None:
        self.Status = grpclib.client.UnaryUnaryMethod(
            channel,
            '/ModzyModel/Status',
            openmodel.v1.model_pb2.StatusRequest,
            openmodel.v1.model_pb2.StatusResponse,
        )
        self.Run = grpclib.client.UnaryUnaryMethod(
            channel,
            '/ModzyModel/Run',
            openmodel.v1.model_pb2.RunRequest,
            openmodel.v1.model_pb2.RunResponse,
        )
        self.Shutdown = grpclib.client.UnaryUnaryMethod(
            channel,
            '/ModzyModel/Shutdown',
            openmodel.v1.model_pb2.ShutdownRequest,
            openmodel.v1.model_pb2.ShutdownResponse,
        )
