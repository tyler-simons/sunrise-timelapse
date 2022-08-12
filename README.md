# Sunrise-Timelapse for Raspberry Pi

This repository contains code to help run your Raspberry Pi HQ camera module as a timelapse camera, upload the GIF to the cloud, and send you a text message containing the GIF. I have set up a camera on my patio and every morning I get a gif sent to me of the sunrise over the bay area. 

An example of a gif generated using this repo can be found here: [Sunrise gif](https://www.googleapis.com/download/storage/v1/b/timelapses/o/20220728.gif?generation=1659020680609107&alt=media)

This project integrates the following technologies:
1. Raspberry Pi (camera operations)
2. Google Cloud Storage (gif file storage)
3. Google Cloud Functions (message delivery and notification)
4. Twilio (message delivery and notification)

The repository helps the pi run a timelapse camera, taking images every few seconds, compiling them into a GIF and uploading to cloud storage. 
Once this is done, it triggers a cloud function to populate a text message with 

## Installation

Python >3.8 is recommended on your local computer and on the raspberry pi. 
To start, clone the repository onto the pi. 

```bash
git clone https://github.com/tyler-simons/sunrise-timelapse.git
```

Then create a virtual environment to run the script and install the requirements

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To run the Google Cloud portion of this project, you will need to create a project that has the google cloud storage and google cloud functions API enabled. Then you need to download a .json file containing an API key. Instructions on how to do this can be found [here](https://cloud.google.com/iam/docs/creating-managing-service-account-keys)

You can set up the gcloud command line tool to automatically deploy the cloud function from the repo on the pi. Directions to install that are found [here](https://cloud.google.com/sdk/docs/install). You can sign in and then deploy the cloud function automatically with

```bash
sh deploy_text_timelapse.sh
```

The next step would be to set up a [twilio account](https://www.twilio.com/) and get a phone number from which to send the notifier messages. I currently operate on a trial twilio account which was free to set up. Info on their python API can be found [here](https://www.twilio.com/docs/libraries/python).

## Usage
Once everything has been set up and configued in the YAML file, make sure that you transfer the API .json file from your local computer to the raspberry pi. You can do this using [scp](https://howchoo.com/pi/how-to-transfer-files-to-the-raspberry-pi).

Set up a cronjob to run the sunrise.py file. Directions on how to do that are located [here](https://bc-robotics.com/tutorials/setting-cron-job-raspberry-pi/). With your pi running, the photos will be taken, saved, compiled, uploaded, and messaged! Enjoy your new timelapse camera!

## Contributing
Pull requests are welcome to improve the usability of the repo. 

## License
[MIT](https://choosealicense.com/licenses/mit/)
