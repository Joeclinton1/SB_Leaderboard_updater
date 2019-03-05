from __future__ import print_function
import urllib.request
import json
from urllib.request import Request
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request as auth_request
import time
def getService():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(auth_request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)

def updateLeaderboard(rows, username,points):
    if [username] in rows:
        print("update")
        cellPos = points_tab + '!C'+str(rows.index([username]))
        sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range=cellPos,
            valueInputOption='USER_ENTERED',
            body={'values': [[int(points)]]}
        ).execute()
    else:
        print("append")
        sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range=points_tab+'!B:B',
            valueInputOption='USER_ENTERED',
            insertDataOption='OVERWRITE',
            body={'values': [["",username,int(points)]]}
        ).execute()


api_url = "https://www.youtube.com/live_chat/get_live_chat?continuation=0ofMyAOOARogQ2c4S0RRb0xiVk5SU1ZoZlJ6TlVhbFVnQVElM0QlM0Qo-dPN3Z3p4AIwADgAQAJKLggAEAAYACAAKg5zdGF0aWNjaGVja3N1bToFGMDDkwdAAEoAUJXGm8Wd6eACWANQtZaF3p3p4AJY0sDKyJvp4AJoBIIBBAgEEACIAQCaAQIIAKAB1Let3p3p4AI%253D&pbj=1&last=1"
headers = {"authority": 'www.youtube.com','method': 'GET','scheme': 'https','accept': '*/*', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'}
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
spreadsheet_id = '1cBMj7yhF7MQz9VSJME8eAt4TWbZsa2WDX3B9eCQiTt8' #Change this to the id of the spreadsheet found at the end of the url.
q = Request(api_url, headers=headers)
oldMessage = ""
service = getService()
sheet = service.spreadsheets()
points_tab = "Points leaderboard" #name of tab with points leaderboard

def main():
    while 1:
        parsed = json.loads(urllib.request.urlopen(q).read())
        # print(json.dumps(parsed, indent=4, sort_keys=True))
        actions = parsed['response']['continuationContents']['liveChatContinuation']['actions']

        rows = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=points_tab+'!B:B'
        ).execute().get('values')
        print(rows)

        for action in actions:
                try:
                    chatItem = action['addChatItemAction']['item']['liveChatTextMessageRenderer']
                    mData = (chatItem['authorName']['simpleText'],chatItem['message']['simpleText']) #mData = message data

                    if mData[0] == 'Streamlabs':
                        pData = (mData[1].split(',')[0][1:],mData[1].split()[-2]) #pData = points data
                        updateLeaderboard(rows,pData[0],pData[1])
                        #print("User: " + pData[0] +" has " + pData[1] + " points.")
                except Exception as e:
                    print(e)
        time.sleep(5)

if __name__ == '__main__':
    main()