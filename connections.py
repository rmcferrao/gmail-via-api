#%%
from __future__ import print_function
from collections import defaultdict 
import pandas as pd
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import nltk
import re
from nltk.corpus import stopwords

print('IMPORTING PACKAGES AND DEFINING FUNCTIONS')

def load_creds():
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    return creds

def minimal_from_id(service, ide):
    message_json = service.users().messages().get(  id=ide, 
                                                    userId='me', 
                                                    format='metadata', 
                                                    # metadataHeaders='From'
                                                    ).execute()
    
    d = {el['name']:el['value'] for el in message_json['payload']['headers']}
    message_json['from'] = d['From']
    message_json['Subject'] = d['Subject']

    message_json.pop('payload')

    return message_json

def list_message_ids(service, **kwargs):
    return  service.users().messages().list(userId='me', 
                                            includeSpamTrash=True,
                                            **kwargs,
                                            ).execute()  

def args_dic(maxResults=10, pattern = None, labelIds = None, pageToken = None):
    return  {'maxResults': maxResults,
            'q': pattern,
            'labelIds': labelIds,
            'pageToken': pageToken}

#%%
## Get necessary info to make an educated guess
print('LOADING CREDENTIALS AND BUILDING API SERVICE')
creds = load_creds()
service = build('gmail', 'v1', credentials=creds)

labels = service.users().labels().list(userId='me').execute()
labels_id_name = {element['id']:element['name'] for element in labels['labels']}

#%%
# search pattern
print('API REQUEST LIST OF MESSAGE IDS')

kwargs = args_dic(maxResults=100, 
                  pattern = '{category:promotions category:CLARO} before:01/01/2018')

messages = list_message_ids(service, **kwargs)
nextPageToken = messages['nextPageToken']
numberMessages = messages['resultSizeEstimate']

messages_minimal = [minimal_from_id(service, ide['id']) for ide in messages['messages']]

#%%
# Label Name
print('FORMATING/CLEANING DATA')

df = pd.DataFrame(messages_minimal)
id_to_name = lambda x: [labels_id_name[xi] for xi in x]
df['labelName'] = df.labelIds.map(id_to_name)

# Cleanning
df = pd.concat([df, 
                df['from'].str.extract(r'(?P<fromEmail>[\w_\.-]+@[\w_\.-]+)'),
                df['from'].str.extract(r'(?P<fromName>.+)"?\s\S+@\S+')], 
                axis=1)

df['fromName'] = df['fromName'].str.replace('"', '', regex=False)
df['size (kb)'] = df['sizeEstimate'] / 1000
df['date'] = pd.to_datetime(df.internalDate, unit='ms')

df.drop(columns=['from', 'sizeEstimate', 'internalDate', 'historyId', 'threadId'], inplace=True)



#%%
# Criterias
df.labelName.map(lambda x: True if 'DRAFT' in x else False)
df.fromEmail.str.contains(r'\S+youtube\S*', flags=re.IGNORECASE)
# %%

# Removing stop words
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
nltk.download('stopwords') 
nltk.download('punkt')

stop_words = set(stopwords.words('portuguese')) 

text = df.snippet.str.lower()[0]

# tokens of words  
tokenizer = RegexpTokenizer(r'\w+')
word_tokens = tokenizer.tokenize(text)
    
filtered_sentence = [] 
  
for w in word_tokens: 
    if w not in stop_words: 
        filtered_sentence.append(w) 


print("\n\nOriginal Sentence \n\n")
print(" ".join(word_tokens)) 

print("\n\nFiltered Sentence \n\n")
print(" ".join(filtered_sentence)) 




# %%

# %%
