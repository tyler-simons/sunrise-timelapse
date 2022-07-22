from picamera import PiCamera
import time
from datetime import datetime as dtdt
import datetime
import imageio.v2 as imageio
import os, shutil
from google.cloud import storage
from google.oauth2 import service_account
import yaml
from pathlib import Path

# Clear out the folder
def clean_timelapse_folder( path_to_photo_folder:str):
    """Remove all of the files from the folder path specified in the arguments
    Args:
        path_to_photo_folder (str): The full path to the folder that should be cleaned
    Returns:
        str: Success
    """    
    for filename in os.listdir(path_to_photo_folder):
        file_path = os.path.join(path_to_photo_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    return "Success"


def perform_timelapse(path_to_photo_folder:str, hour_end:int, timelapse_wait:int):
    """ Have the picamera take the timelapse photos and store them as jpg files. 

    Args:
        path_to_photo_folder (str): The full filepath to the folder where the jpg files are to be captured
        hour_end (int): Hour from 1 to 24 of when you would like the timelapse to start
        timelapse_wait (int): Seconds to wait between timelapse photos
    """    
    while int(hour_end) > dtdt.now().hour:
        # Initalize the camera
        camera = PiCamera()
        camera.resolution = (1024, 768)
        camera.start_preview()

        # Create the filename and annotation
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Capture the photo
        time.sleep(2)
        camera.capture(path_to_photo_folder+f"{timestamp}.jpg")
        print("Photo Taken")
        camera.close()

        # Wait
        time.sleep(timelapse_wait)

    return "Timelapse take"

def get_files_in_order(dirpath:str, sort_by="time_modified"):
    """Get files in a directory returned as a list in creation order or in filename order. 

    Args:
        dirpath (str): _description_

    Returns:
        _type_: _description_
    """    ''''''
    a = [s for s in os.listdir(dirpath)
         if os.path.isfile(os.path.join(dirpath, s))]
    
    if sort_by=="time_modified":  
        a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)))
        return a
    elif sort_by=="filename":
        return sorted(a)
    else:
        raise


def make_gif_from_jpgs(path_to_photo_folder:str):
    """Given a path to a folder, create a GIF from the .jpg files in the folder. The files will be joined together based on their creation time. 

    Args:
        path_to_photo_folder (str): _description_
    """    
    images = []
    sorted_pics = get_files_in_order(path_to_photo_folder)

    # Iterate through the images
    for filename in sorted_pics:
        if filename.endswith('.jpg'):
            images.append(imageio.imread(path_to_photo_folder+filename))

    todays_date = datetime.datetime.now().strftime("%Y%m%d")
    gif_name = f'{todays_date}.gif'

    gif_path = path_to_photo_folder + gif_name
    imageio.mimsave(gif_path, images, fps=5)

    return gif_path


def push_gif_to_GCP(path_to_gif:str, gcp_key_path:str, gcp_project:str, gcp_gcs_bucket:str):
    """ Push the GIF up to google cloud storage (GCS)

    Args:
        path_to_gif (str): File path for where the gif is stored
        gcp_key_path (str): File path to where the GCP JSON file is stored
        gcp_project (str): Name of the GCP project that the GCP key is associated with
        gcp_gcs_bucket (str): Name of the GCS bucket where the GIF should be stored
    """
    # Extract the base name
    gif_name = os.path.basename(path_to_gif)

    # Authorize and connect
    credentials = service_account.Credentials.from_service_account_file(gcp_key_path)
    storage_client = storage.Client(project=gcp_project, credentials=credentials)
    bucket = storage_client.bucket(gcp_gcs_bucket)

    # Create the blob and upload the file
    blob = bucket.blob(gif_name)
    blob.upload_from_filename(path_to_gif, timeout=300)

    return(f"File {gif_name} uploaded to {gcp_gcs_bucket}.")

def main():

    print("Starting timelapse camera")

    # Load in the yaml file as env variables
    conf = yaml.safe_load(Path('config.yaml').read_text())
    for key, value in conf.items():
        os.environ[key]=value

    # Define our config variables
    clean_timelapse_folder = os.getenv('CLEAN_TIMELAPSE_FOLDER')
    path_to_photo_folder =  os.getenv('PATH_TO_PHOTO_FOLDER')
    hour_end =  os.getenv('HOUR_END')
    gcp_key_path =  os.getenv('GCP_KEY_PATH')
    gcp_gcs_bucket =  os.getenv('GCP_GCS_BUCKET')
    timelapse_wait =  os.getenv('TIMELAPSE_WAIT')
    gcp_project =  os.getenv('GCP_PROJECT')

    # Clean timelapse folder to make room for new files
    if clean_timelapse_folder:
        clean_timelapse_folder(path_to_photo_folder)
    
    # Perform the timelapse
    perform_timelapse(path_to_photo_folder, hour_end, timelapse_wait)
    print("Timelapse done")
    
    # Make the gif and get the path
    path_to_gif = make_gif_from_jpgs(path_to_photo_folder)
    print("GIF created")

    # Push into GCP
    push_gif_to_GCP(path_to_gif, gcp_key_path, gcp_project, gcp_gcs_bucket)
    print("GIF pushed")

if __name__ == "__main__":
    main()

