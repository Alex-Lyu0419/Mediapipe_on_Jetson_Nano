# Run this python script on your PC (client) and connect to jetson nano (server) via grpc
import grpc
import argparse
import LivePlayer_pb2
import LivePlayer_pb2_grpc

ADDR = '192.168.55.1'
PORT = 50051

def run(detect):
    with grpc.insecure_channel(f'{ADDR}:{PORT}') as channel:
        print("-------------- Client Running --------------")

        stub = LivePlayer_pb2_grpc.LivePlayerStub(channel)
        new_type = LivePlayer_pb2.Types(type = detect)
        final_result = stub.LiveStream(new_type)

        print(final_result.result_number)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", type=str, help="please type in hand, face, mesh, or pause")
    args = parser.parse_args()
    run(args.type)