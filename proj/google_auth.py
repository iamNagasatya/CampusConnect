import requests

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError


client_id = "258205076364-on681od4ciorkkhgbuj1qesefmrk13i5.apps.googleusercontent.com"
client_secret = "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"

def get_tokens(authcode):
    url = "https://oauth2.googleapis.com/token"
    data = {
        "code" : authcode,
        "client_id" : client_id,
        "client_secret" : client_secret,
        "grant_type" : "authorization_code",
        "redirect_uri" : "http://localhost:8000/google_auth"
    }
    resp = requests.post(url, data=data)

    return resp.json()


def refresh_access_token(refresh_token):
    url = "https://oauth2.googleapis.com/token"
    data = {
        "refresh_token" : refresh_token,
        "client_id" : "258205076364-on681od4ciorkkhgbuj1qesefmrk13i5.apps.googleusercontent.com",
        "client_secret" : "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",
        "grant_type" : "refresh_token",
    }
    resp = requests.post(url, data=data)
    data = resp.json()
    print(data)
    access_token = data.get("access_token")
    if access_token:
        return (True, access_token)
    return (False, data.get("error"))

def create_creds(access_token, refresh_token):
    client_id = "258205076364-on681od4ciorkkhgbuj1qesefmrk13i5.apps.googleusercontent.com"
    client_secret = "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"


    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token", 
        client_id=client_id,
        client_secret=client_secret,
    )
    return creds


def create_event(creds, task):
    try:
        service = build("calendar", "v3", credentials=creds)

        event = {
          'summary': task.name,
          'description': task.description,
          'start': {
            'dateTime': task.scheduled_at.isoformat(timespec="seconds"),
          },
          'end': {
            'dateTime': (task.scheduled_at + task.duration).isoformat(timespec="seconds"),
          },
          'reminders': {
            'useDefault': False,
            'overrides': [
              {'method': 'popup', 'minutes': 5},
            ],
          },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print ('Event created: %s' % (event.get('htmlLink')))
        return event.get("id")

    except Exception as error:
        print(f"An error occurred: {error}")


def update_event(creds, task, event_id):
    try:
        service = build("calendar", "v3", credentials=creds)

        event = {
          'summary': task.name,
          'description': task.description,
          'start': {
            'dateTime': task.scheduled_at.isoformat(timespec="seconds"),
          },
          'end': {
            'dateTime': (task.scheduled_at + task.duration).isoformat(timespec="seconds"),
          },
          'reminders': {
            'useDefault': False,
            'overrides': [
              {'method': 'popup', 'minutes': 5},
            ],
          },
          
        }

        event = service.events().update(calendarId='primary', body=event, eventId=event_id).execute()
        print ('Event Updated: %s' % (event.get('htmlLink')))
        return event.get("id")

    except Exception as error:
        print(f"An error occurred: {error}")


def delete_event(creds, event_id):
    try:
        service = build("calendar", "v3", credentials=creds)

        service.events().delete(calendarId='primary', eventId=event_id).execute()

    except Exception as error:
        print(f"An error occurred: {error}")


def batchPush(creds, tasks):
    try:
        service = build("calendar", "v3", credentials=creds)

        for task in tasks:

          event = {
            'summary': task.name,
            'description': task.description,
            'start': {
              'dateTime': task.scheduled_at.isoformat(timespec="seconds"),
            },
            'end': {
              'dateTime': (task.scheduled_at + task.duration).isoformat(timespec="seconds"),
            },
            'reminders': {
              'useDefault': False,
              'overrides': [
                {'method': 'popup', 'minutes': 5},
              ],
            },
          }
          if task.event_id:
              event = service.events().update(calendarId='primary', body=event, eventId=task.event_id).execute()
              print ('Event Updated: %s' % (event.get('htmlLink')))
          else:
              event = service.events().insert(calendarId='primary', body=event).execute()
              print ('Event created: %s' % (event.get('htmlLink')))

          task.event_id = event.get("id")
          task.save()

    except Exception as error:
        print(f"An error occurred: {error}")