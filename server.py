import cv2
import grpc
import time
import LivePlayer_pb2
import LivePlayer_pb2_grpc
import multiprocessing as mp
import mediapipe as mp2
from concurrent import futures

PORT = 50051

class Mediapipe_Process():
    def __init__(self):
        self.mp_drawing = mp2.solutions.drawing_utils
        self.mp_drawing_styles = mp2.solutions.drawing_styles
        self.mp_hands = mp2.solutions.hands
        self.mp_faces = mp2.solutions.face_detection
        self.mp_mesh = mp2.solutions.face_mesh

        self.proc_type = 0
        self.proc_type_name = 'default'

    def hand_proc(self, frame):
        results = self.mp_hands.Hands(min_detection_confidence=0.3, min_tracking_confidence=0.3, max_num_hands = 1).process(frame)
        # Draw landmakrs
        if (results.multi_hand_landmarks):
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                print("draw hand")
            print("finish draw hand")

        return frame

    def face_proc(self, frame):
        results = self.mp_faces.FaceDetection(min_detection_confidence=0.5).process(frame)
        # Draw landmakrs
        if (results.detections):
            for detection in results.detections:
                self.mp_drawing.draw_detection(frame, detection)
                print("draw face")
            print("finish draw face")

        return frame

    def mesh_proc(self, frame):
        results = self.mp_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.2, min_tracking_confidence=0.2).process(frame)
        # Draw landmakrs
        if (results.multi_face_landmarks):
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
                    )

                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
                    )

                print("draw mesh")
            print("finish draw mesh")

        return frame

    def change_type(self, change_type):
        print(f'Change type from {self.proc_type_name} to {change_type}')
        
        self.proc_type_name = change_type
        if (change_type == 'hand'):
            self.proc_type = 1
        elif (change_type == 'face'):
            self.proc_type = 2
        elif (change_type == 'mesh'):
            self.proc_type = 3
        else:
            self.proc_type = 0


    def run_process(self, frame):
        if (self.proc_type == 1):
            frame = self.hand_proc(frame)
        elif (self.proc_type == 2):
            frame = self.face_proc(frame)
        elif (self.proc_type == 3):
            frame = self.mesh_proc(frame)
        
        return frame

mp_process = Mediapipe_Process()

class MyStreamServicer(LivePlayer_pb2_grpc.LivePlayerServicer):
    """Provides methods that implement functionality of route guide server."""

    def LiveStream(self, request, context):
        global mp_process

        print(request)
        results = request.type
        mp_process.change_type(results)

        if results == 'hand':
            new_result = LivePlayer_pb2.Results(result_number=1)
        elif results == 'face':
            new_result = LivePlayer_pb2.Results(result_number=2)
        elif results == 'mesh':
            new_result = LivePlayer_pb2.Results(result_number=3)
        else:
            new_result = LivePlayer_pb2.Results(result_number=0)
        return new_result

def serve(queue):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    LivePlayer_pb2_grpc.add_LivePlayerServicer_to_server(MyStreamServicer(), server)
    server.add_insecure_port(f'[::]:{PORT}')
    server.start()

    gstreamer_rtmpstream(queue)

    server.wait_for_termination()

def gstreamer_camera(queue):
    # Use the provided pipeline to construct the video capture in opencv
    pipeline = (
        "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)1920, height=(int)1080, "
            "format=(string)NV12, framerate=(fraction)30/1 ! "
        "queue ! "
        "nvvidconv flip-method=2 ! "
            "video/x-raw, "
            "width=(int)1920, height=(int)1080, "
            "format=(string)BGRx, framerate=(fraction)30/1 ! "
        "videoconvert ! "
            "video/x-raw, format=(string)BGR ! "
        "appsink"
    )

    # Complete the function body
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    time.sleep(1)
    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print('no camera')
                break

            queue.put(frame)

    except KeyboardInterrupt as e:
        cap.release()

def gstreamer_rtmpstream(queue):
    
    global mp_process

    # Use the provided pipeline to construct the video writer in opencv
    pipeline = (
        "appsrc ! "
            "video/x-raw, format=(string)BGR ! "
        "queue ! "
        "videoconvert ! "
            "video/x-raw, format=RGBA ! "
        "nvvidconv ! "
        "nvv4l2h264enc bitrate=8000000 ! "
        "h264parse ! "
        "flvmux ! "
        'rtmpsink location="rtmp://localhost/rtmp/live live=1"'
    )
    # Complete the function body

    p = mp.Process(target=gstreamer_camera, args=(queue,))
    p.start()
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(pipeline, apiPreference=cv2.CAP_GSTREAMER, fourcc=fourcc, fps=30.0, frameSize=(1920, 1080))
    count = 0

    time.sleep(1)

    while count < 10000:
        #print(count)

        if queue.empty():
            continue

        frame = queue.get()

        if(count%3 == 0):
            frame = mp_process.run_process(frame)

        out.write(frame)
        count+=1
        print(count)
        
    p.terminate()
    p.join()

    print('finish')


if __name__ == '__main__':

    queue = mp.Queue()
    serve(queue)