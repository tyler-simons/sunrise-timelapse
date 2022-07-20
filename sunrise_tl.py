from picamera import PiCamera
import time
from datetime import datetime as dtdt
import datetime
import imageio.v2 as imageio
import os, shutil
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials

time_start = 5
time_end = 9
photo_folder = "/home/pi/sunrises/"
GCP_KEY_PATH = "./tylerpersonalprojects-362a1ae72b01.json"
GCP_PROJECT = "tylerpersonalprojects"
GCP_GCS_BUCKET = "timelapseposter"

# Clear out the folder
for filename in os.listdir(photo_folder):
    file_path = os.path.join(photo_folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

# Take the pictures
while int(time_end) > dtdt.now().hour:
    camera = PiCamera()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%S")
    camera.capture(photo_folder+f"{timestamp}.jpg")
    time.sleep(60)
    print("Photo Taken")

# Compile into a gif
images = []
for filename in photo_folder:
    images.append(imageio.imread(filename, plugin='DICOM'))

todays_date = datetime.datetime.now().strftime("%Y%m%d")
gif_name = photo_folder+f'{todays_date}.gif'
imageio.mimsave(gif_name, images)

# Push to GCP
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    GCP_KEY_PATH
)
client = storage.Client(credentials=credentials, project=GCP_PROJECT)
bucket = client.get_bucket(GCP_GCS_BUCKET)
blob = bucket.blob(GCP_GCS_BUCKET)
blob.upload_from_filename(gif_name)
