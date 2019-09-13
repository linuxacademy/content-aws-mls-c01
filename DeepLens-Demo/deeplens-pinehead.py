# Developed from code sourced from:
# Copyright Amazon AWS DeepLens, 2017
# Copyright Amazon AWS DeepLens, 2018
# And Mike Chambers @ Linux Academy

import os
import greengrasssdk
from threading import Timer, Thread, Event
import time
import awscam
import cv2
import mo
import json
import numpy as np


class LocalDisplay(Thread):

    def __init__(self, resolution):
        # Initialize the base class, so that the object can run on its own
        # thread.
        super(LocalDisplay, self).__init__()
        # List of valid resolutions
        RESOLUTION = {'1080p' : (1920, 1080), '720p' : (1280, 720), '480p' : (858, 480)}
        if resolution not in RESOLUTION:
            raise Exception("Invalid resolution")
        self.resolution = RESOLUTION[resolution]
        # Initialize the default image to be a white canvas. Clients
        # will update the image when ready.
        self.frame = cv2.imencode('.jpg', 255*np.ones([640, 480, 3]))[1]
        self.stop_request = Event()

    def run(self):
        # Path to the FIFO file. The lambda only has permissions to the tmp
        # directory. Pointing to a FIFO file in another directory
        # will cause the lambda to crash.
        result_path = '/tmp/results.mjpeg'
        # Create the FIFO file if it doesn't exist.
        if not os.path.exists(result_path):
            os.mkfifo(result_path)
        # This call will block until a consumer is available
        with open(result_path, 'w') as fifo_file:
            while not self.stop_request.isSet():
                try:
                    # Write the data to the FIFO file. This call will block
                    # meaning the code will come to a halt here until a consumer
                    # is available.
                    fifo_file.write(self.frame.tobytes())
                except IOError:
                    continue

    def set_frame_data(self, frame):
        ret, jpeg = cv2.imencode('.jpg', cv2.resize(frame, self.resolution))
        if not ret:
            raise Exception('Failed to set frame data')
        self.frame = jpeg

    def join(self):
        self.stop_request.set()

def greengrass_infinite_infer_run():
    try:
        input_width = 224
        input_height = 224

        model_name = "image-classification"
        model_type = "classification"

        client = greengrasssdk.client('iot-data')

        iotTopic = '$aws/things/{}/infer'.format(os.environ['AWS_IOT_THING_NAME'])

        local_display = LocalDisplay('480p')
        local_display.start()

        error, model_path = mo.optimize(model_name,input_width,input_height, aux_inputs={'--epoch': 30})
        mcfg = {"GPU": 1}

        print("model_path: " + model_path)

        model = awscam.Model(model_path, mcfg)

        client.publish(topic=iotTopic, payload="Model loaded")

        with open('pinehead_labels.txt', 'r') as f:
            labels = [l.rstrip() for l in f]

        num_top_k = 2

        # Send a starting message to IoT console
        client.publish(topic=iotTopic, payload="Inference is starting")

        doInfer = True
        while doInfer:
            # Get a frame from the video stream
            ret, frame = awscam.getLastFrame()
            # Raise an exception if failing to get a frame
            if ret == False:
                raise Exception("Failed to get frame from the stream")

            # Resize frame to fit model input requirement
            s = frame.shape
            cropped = frame[0:s[0], int((s[1]-s[0])/2):s[0]+int((s[1]-s[0])/2)]
            frameResize = cv2.resize(cropped, (input_width, input_height))

            # Run model inference on the resized frame
            inferOutput = model.doInference(frameResize)

            parsed_inference_results = model.parseResult(model_type, model.doInference(frameResize))

            top_k = parsed_inference_results[model_type][0:num_top_k-1]

            msg  = "{"
            msg += '"{}"'.format(labels[top_k[0]["label"]])
            msg += "}"

            client.publish(topic=iotTopic, payload = msg)

            font = cv2.FONT_HERSHEY_SIMPLEX
            
            cv2.putText(frame, labels[top_k[0]["label"]], (10, 140), font, 5, (174, 235, 52), 10)
            local_display.set_frame_data(frame)


    except Exception as e:
        msg = "myModel Lambda failed: " + str(e)
        client.publish(topic=iotTopic, payload=msg)

    # Asynchronously schedule this function to be run again in 15 seconds
    Timer(15, greengrass_infinite_infer_run).start()

# Execute the function above
greengrass_infinite_infer_run()

# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
    return
