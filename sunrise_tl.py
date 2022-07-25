from picamera import PiCamera
import time
from datetime import datetime as dtdt
import datetime
import imageio.v2 as imageio
import os, shutil
from google.cloud import storage
from google.oauth2 import service_account


print("Starting timelapse camera")
time_end = 8
photo_folder = "/home/pi/sunrises/"
GCP_KEY_PATH = "./tylerpersonalprojects-362a1ae72b01.json"
GCP_PROJECT = "tylerpersonalprojects"
GCP_GCS_BUCKET = "timelapses"
delete_folder = True
timelapse_wait = 60

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
while int(time_end) > dtdt.now().hour:
    camera = PiCamera()
    camera.resolution = (2592, 1944)
    camera.start_preview()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time.sleep(2)
    camera.capture(photo_folder+f"{timestamp}.jpg")
    print("Photo Taken")
    camera.close() 
    time.sleep(timelapse_wait)

# Compile into a gif

def getfiles(dirpath):
    a = [s for s in os.listdir(dirpath)
         if os.path.isfile(os.path.join(dirpath, s))]
    a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)))
    return a

# Get sorted files by creation time
images = []
sorted_pics = getfiles(photo_folder)

for filename in sorted_pics:
    if filename.endswith('.jpg'):
        images.append(imageio.imread(photo_folder+filename))

todays_date = datetime.datetime.now().strftime("%Y%m%d")
gif_name = f'{todays_date}.gif'

imageio.mimsave(photo_folder + gif_name, images, fps=5)


# Push to GCP
credentials = service_account.Credentials.from_service_account_file(GCP_KEY_PATH)
storage_client = storage.Client(project=GCP_PROJECT, credentials=credentials)
bucket = storage_client.bucket(GCP_GCS_BUCKET)
blob = bucket.blob(gif_name)

blob.upload_from_filename(photo_folder+gif_name, timeout=300)

print(
    f"File {gif_name} uploaded to {GCP_GCS_BUCKET}."
)

