from twilio.rest import Client
import os


def send_twilio_message(
    message_body: str,
    account_sid: str,
    auth_token: str,
    from_number: str,
    to_number: str,
):
    """Send a text message to a phone number from a twilio account
    Args:
        message_body (str): Text to show up in the message
        account_sid (str): Twilio account SID
        auth_token (str): Twilio account auth token
        from_number (str): Twilio provided phone number
        to_number (str): Phone number to send the message to

    Returns:
        str: Message sent success
    """
    client = Client(account_sid, auth_token)
    message = client.messages.create(body=message_body, from_=from_number, to=to_number)

    return f"Message Sent: {message.sid}"


def text_new_addition(event, context):
    """Send a twilio text triggered by a change to a Cloud Storage bucket about the new gif
    Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """

    # Globals as env vars
    ACCOUNT_SID = os.getenv("ACCOUNT_SID")
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")
    FROM_NUMBER = os.getenv("FROM_NUMBER")
    TO_NUMBER = os.getenv("TO_NUMBER")

    message = (
        f"Good morning! Here is the sunrise for this morning: {event['mediaLink']}"
    )
    send_twilio_message(message, ACCOUNT_SID, AUTH_TOKEN, FROM_NUMBER, TO_NUMBER)
