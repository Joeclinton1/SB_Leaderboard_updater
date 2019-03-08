import urllib.request
import json
from urllib.request import Request
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request as auth_request
import time
import itertools


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


def updateLeaderboard(rows, pData):
    flatRows = list(itertools.chain.from_iterable(rows))
    oldUsers = set(flatRows) & set(pData.keys())
    newUsers = set(pData.keys()) - set(flatRows)
    data = []
    for username in oldUsers:
        data.append(
            {
                'range': points_tab + '!C' + str(rows.index([username]) + 1),
                'values': [[pData[username]]]
            }
        )
    for i, username in enumerate(newUsers):
        r = len(rows) + i + 1
        data.append(
            {
                'range': points_tab + '!A' + str(r),
                'values': [[
                    "=ROW()-2",
                    username,
                    pData[username],
                    "=(C%s - C%s) * 5" % (str(r), str(r + 1)),
                    "=D%s / 60" % str(r),
                    "=(1000 - C%s) * 5" % str(r),
                    "=C%s * 5" % str(r),
                    "=G%s / 60" % str(r),
                    "=H%s / 24" % str(r),
                    "= C%s - C%s" % (str(r - 1), str(r)),
                    "=C$3 - C%s" % str(r),
                    "= G%s / G$2" % str(r)

                ]]
            }
        )
    sheet.values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
    ).execute()


api_url = "https://www.youtube.com/live_chat/https://www.youtube.com/live_chat/get_live_chat?continuation=0ofMyAOiARo0Q2lNU0lRb1lWVU5rUzB4a09XWmZPRnA1UkZOTGVFMXRNVFp2VW5kM0VnVXZiR2wyWlNBQijsxcLhuu_gAjAAOABAAkouCAAQABgAIAAqDnN0YXRpY2NoZWNrc3VtOgUYwMOTB0AASgBQq_7V6brv4AJYA1CH1rHiuu_gAlimnNm9h-7gAmgEggEECAQQAIgBAJoBAggAoAHPmrb2uu_gAg%253D%253D&pbj=1"
headers = {"authority": 'www.youtube.com', 'method': 'GET', 'scheme': 'https', 'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'}
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
spreadsheet_id = '1a-idt5GvfRHkrE-SGX8o3Hy5D9smloUeyUG8rhBlaWI'  # Change this to the id of the spreadsheet found at the end of the url.
q = Request(api_url, headers=headers)
oldMessage = ""
service = getService()
sheet = service.spreadsheets()
points_tab = "Points leaderboard"  # name of tab with points leaderboard


def main():
    while 1:
        parsed = json.loads(urllib.request.urlopen(q).read())
        # print(json.dumps(parsed, indent=4, sort_keys=True))
        actions = parsed['response']['continuationContents']['liveChatContinuation']['actions']

        rows = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=points_tab + '!B:B'
        ).execute().get('values')
        pData = {}
        for action in actions:
            try:
                chatItem = action['addChatItemAction']['item']['liveChatTextMessageRenderer']
                mData = (
                    chatItem['authorName']['simpleText'], chatItem['message']['simpleText'])  # mData = message data

                if mData[0] == 'Jay Burton' and mData[1].split()[-2]=="points":
                    username = " ".join(mData[1].split('You')[0][1:].split()[:2])
                    points = mData[1].split()[-2]
                    pData[username] = points  # pData = points data
                    print("User: %s has %s points." % (username,points))
            except:
                pass
        print("")
        updateLeaderboard(rows, pData)
        time.sleep(5)


if __name__ == '__main__':
    main()
