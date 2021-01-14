#%%
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://mail.google.com/']

"""Shows basic usage of the Gmail API.
Lists the user's Gmail labels.
"""
creds = None
gmail_url = 'https://gmail.googleapis.com/gmail/v1/users/'
userId = 'rmouracruz@gmail.com'

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

service = build('gmail', 'v1', credentials=creds)

# Call the Gmail API

results = service.users().labels().list(userId=userId).execute()
labels = results.get('labels', [])




print()
#%%