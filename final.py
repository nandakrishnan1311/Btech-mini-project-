from twilio.rest import Client
from imutils.video import VideoStream
from threading import Thread
import numpy as np
import argparse
import imutils
import time
import cv2
from playsound import playsound
import requests

# Your Twilio Account SID and Auth Token
account_sid = 'xxxxxxx'
auth_token = 'xxxxxx'

# Your Google Maps API key
api_key = "xxxxxx"

# Create a Twilio client
client = Client(account_sid, auth_token)

# Your Twilio phone number and the recipient's phone number
from_number = 'xxxxxx'
to_number = 'xxxxxx'

def get_coordinates(address):
    endpoint = "https://maps.googleapis.com/maps/apixxxxxxx"
    params = {
        "address": address,
        "key": api_key
    }
    response = requests.get(endpoint, params=params)
    data = response.json()
    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        return None, None

def send_message_and_call():
    # Additional information for the message
    emergency_message = "EMERGENCY MESSAGE"
    accident_message = "emergency ! one vehicle is under accident please help them!"
    vehicle_number = "KL31A1234"
    address = endpoint  # Example address

    # Get coordinates for the address
    lat, lng = get_coordinates(address)
    if lat is not None and lng is not None:
        location = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
    else:
        location = "Location not available"

    # Construct the message body
    message_body = f"{emergency_message}\n{accident_message}\n{vehicle_number}\n{location}"

    # Send the message
    message = client.messages.create(
        body=message_body,
        from_=from_number,
        to=to_number
    )

    print("Message sent successfully!")

    # Wait for 30 seconds before making the call
    time.sleep(30)

    # Message to be spoken during the call
    call_message = "Alert! Emergency message. One vehicle is under accident. Please check message inbox for the vehicle's location. Take immediate action. Thank you."

    # Make the call
    call = client.calls.create(
        twiml=f'<Response><Say>{call_message}</Say></Response>',
        to=to_number,
        from_=from_number
    )

    print("Call initiated successfully! Call SID:", call.sid)

def alarm(msg):
    global alarm_status
    global alarm_status2
    global saying

    while alarm_status:
        print('call')
        # Change the path to your desired audio file
        playsound(r'AUD-20240429-WA0031.mp3')

    if alarm_status2:
        print('call')
        saying = True
        # Change the path to your desired audio file
        playsound(r'AUD-20240429-WA0031.mp3')
        saying = False

    if msg == 'No face detected!':
        # Change the path to your desired audio file for face detection alert
        playsound(r'AUD-20240429-WA0031.mp3')

def get_yolo():
   model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt', force_reload=True )
   cap = cv2.VideoCapture(0)


def detect_objects(frame, yolo):
   
    pass

# Parse command line arguments
ap = argparse.ArgumentParser()
ap.add_argument("-w", "--webcam", type=int, default=0,
                help="index of webcam on system")
args = vars(ap.parse_args())

# Initialize YOLOv5 detector
yolo = get_yolo()

# Initialize variables
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 30
YAWN_THRESH = 20
FACE_ALERT_FRAMES = 20
alarm_status = False
alarm_status2 = False
saying = False
COUNTER = 0
face_alert_counter = 0

# Start video stream
vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)

while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Perform object detection using YOLOv5
    objects = detect_objects(frame, yolo)

    for obj in objects:
        label, confidence, bbox = obj
        x, y, w, h = bbox
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{label}: {confidence:.2f}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Your existing code for face detection and other functionalities
    # ...

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cv2.destroyAllWindows()
vs.stop()

# Wait for the user to press 'h'
keypress = input("Press 'h' to send emergency message and initiate call: ")

if keypress == 'h':
    send_message_and_call()
else:
    print("Invalid key pressed. Exiting...")
