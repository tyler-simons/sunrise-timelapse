from twilio.rest import Client
import os

def send_twilio_message(message_body:str, ACCOUNT_SID:str, AUTH_TOKEN:str, FROM_NUMBER:str, TO_NUMBER:str):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages \
                    .create(
                        body=message_body,
                        from_=FROM_NUMBER,
                        to=TO_NUMBER
                    )

    return f"Message Sent: {message.sid}"

def text_new_addition(event, context):
    """Send a twilio text triggered by a change to a Cloud Storage bucket about the new gif
    Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """

    # Globals as env vars
    ACCOUNT_SID=os.getenv('ACCOUNT_SID')
    AUTH_TOKEN=os.getenv('AUTH_TOKEN')
    FROM_NUMBER=os.getenv('FROM_NUMBER')
    TO_NUMBER=os.getenv('TO_NUMBER')

    message = f"Good morning! Here is the sunrise for this morning: {event['mediaLink']}"
    send_twilio_message(message, ACCOUNT_SID, AUTH_TOKEN, FROM_NUMBER, TO_NUMBER)