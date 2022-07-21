from picamera import PiCamera
import time
from datetime import datetime as dtdt
import datetime
import imageio.v2 as imageio
import os, shutil
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials

print("Starting timelapse camera")
time_start = 5
time_end = 17
photo_folder = "/home/pi/sunrises/"
GCP_KEY_PATH = "./tylerpersonalprojects-362a1ae72b01.json"
GCP_PROJECT = "tylerpersonalprojects"
GCP_GCS_BUCKET = "timelapses"
delete_folder = True

# Clear out the folder
if delete_folder:
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
while int(time_end) > dtdt.now().minute:
    camera = PiCamera()
    camera.resolution = (1024, 768)
    camera.start_preview()
    # Camera warm-up time
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%S")
    camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time.sleep(2)
    camera.capture(photo_folder+f"{timestamp}.jpg")
    print("Photo Taken")
    camera.close() 
    time.sleep(10)

# Compile into a gif
images = []
for filename in os.listdir(photo_folder):
    images.append(imageio.imread(photo_folder+filename))

todays_date = datetime.datetime.now().strftime("%Y%m%d")
gif_name = f'{todays_date}.gif'

imageio.mimsave(photo_folder + gif_name, images)

# Push to GCP
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    GCP_KEY_PATH
)
client = storage.Client(credentials=credentials, project=GCP_PROJECT)
bucket = client.get_bucket(GCP_GCS_BUCKET)
blob = bucket.blob(gif_name)
blob.upload_from_filename(photo_folder+gif_name)
