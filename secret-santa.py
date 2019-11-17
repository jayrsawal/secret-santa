import sys, getopt
import base64
import random
import pickle
import os.path
import json
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES='https://www.googleapis.com/auth/gmail.send'
def get_creds(creds_file=None, token_file=None):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        print("loading token from file") 
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
       if creds and creds.expired and creds.refresh_token:
           print("refreshing credentials")
           creds.refresh(Request())
       else:
           print("creating authentication token")
           flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
           creds = flow.run_local_server(port=0)
           # Save the credentials for the next run
           with open(token_file, 'wb') as token:
               pickle.dump(creds, token)
    return creds

def get_service(creds):
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

def send_message(service, user_id, message):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    message = (service.users().messages().send(userId=user_id, body=message)
                       .execute())
    return message

def match_targets(service):
    messages = []
    secret_log = {}

    participants = None
    with open('secret-santa.json') as f:
        participants = json.load(f)

    template = "%(name)s: %(target)s"
    with open('secret-santa-email', 'r') as f:
        template = f.read()

    targets = list(participants.keys())
    random.shuffle(targets)
    for name in participants:
        email  = participants[name][0]
        group = participants[name][1]
        target = targets.pop()
        while (participants[target][1] == group) and len(targets) > 0:
            targets.append(target)
            random.shuffle(targets)
            target = targets.pop()

        if target == name or group == participants[target][1]:
            return False

        email_body = template % {"name":name.upper(), "target": target.upper()}
        message = create_message("me", email, "OPEN CONTRACT - SECRET SANTA", email_body)
        messages.append(message)
        secret_log[name] = target

    with open('secret_log.json', 'w') as f:
        json.dump(secret_log, f)

    for message in messages:
        response = send_message(service, "me", message)
        print(response)
 
    return True

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"c:t:",["cred=", "token="])
    except getopt.GetoptError:
        print ('secret-santa.py -c <credentials.json> -t <token.pkl>')
    
    creds_file = None
    token_file = None
    for opt, arg in opts:
        if opt == "-c":
            creds_file = arg
        elif opt == "-t":
            token_file = arg

    retries = 5
    service = get_service(get_creds(creds_file, token_file))
    while not match_targets(service) and retries > 0:
        print("Match failed, retrying: {}".format(retries))
        retries = retries - 1


if __name__ == '__main__':
    main(sys.argv[1:])
