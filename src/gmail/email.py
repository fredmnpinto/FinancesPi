import os
import time

from dotenv import load_dotenv
from src.gmail.Google import Create_Service
from os import path
import base64
import tqdm

def construct_service(api_service):
    CLIENT_SERVICE_FILE = 'gmail/client_secret.json'
    # try:
    if api_service == 'drive':
        API_NAME = 'drive'
        API_VERSION = 'v3'
        SCOPES = ['https://www.googlepais.com/auth/drive']
        return Create_Service(CLIENT_SERVICE_FILE, API_NAME, API_VERSION, SCOPES)
    elif api_service == 'gmail':
        API_NAME = 'gmail'
        API_VERSION = 'v1'
        SCOPES = ['https://mail.google.com/']
        return Create_Service(CLIENT_SERVICE_FILE, API_NAME, API_VERSION, SCOPES)
    # except Exception as ex:
    #     print(ex)
    #     return None


def search_email(service, query_string, label_ids):
    try:
        message_list_response = service.users().messages().list(
            userId='me',
            labelIds=label_ids,
            q=query_string
        ).execute()

        message_items = message_list_response.get('messages')
        nextPageToken = message_list_response.get('nextPageToken')

        while nextPageToken:
            message_list_response = service.users().messages().list(
                userId='me',
                labelIds=label_ids,
                pageToken=nextPageToken
            )
            message_items.extend(message_list_response.get('messages'))
            nextPageToken = message_list_response.get('nextPageToken')
        return message_items

    except Exception as ex:
        print(ex)
        return None


def get_message_details(service, message_id, form='metadata', metadata_headers=None):
    if metadata_headers is None:
        metadata_headers = []
    try:
        message_detail = service.users().messages().get(
            userId='me',
            id=message_id,
            format=form,
            metadataHeaders=metadata_headers
        ).execute()
        return message_detail
    except Exception as ex:
        print(ex)
        return None


def download_extratos():
    start_time = time.time()
    """
    Step 1: Connect to gmail
    """
    gmail_service = construct_service('gmail')

    """
    Step 2: Search emails
    """
    query_string = 'Extrato Combinado from:banco@millenniumbcp.pt'
    emails = search_email(gmail_service, query_string, ['INBOX'])

    """
    Step 3: Download emails
    """

    load_dotenv()
    PDF_PATH = os.getenv("PDF_PATH")
    print("{:.2f} since the start of the program".format(time.time() - start_time))
    for e in tqdm.tqdm(emails, desc="Downloading transactions\t", unit="email"):
        messageId = e['threadId']
        messageSubject = '(No subject) ({0})'.format(messageId)
        messageDetail = get_message_details(
            gmail_service,
            e['id'],
            form='full',
            metadata_headers=['parts'])
        messageDetailPayload = messageDetail.get('payload')
        # for item in (messageDetailPayload['headers']):
        # if item['name'] == 'Subject':
        #     if item['value']:
        #         messageSubject = '{0} ({1})'.format(item['value'], messageId)
        #     else:
        #         messageSubject = '(No Subject) ({0})'.format(messageId)
        # print(messageSubject)

        if 'parts' in messageDetailPayload:
            for payload in messageDetailPayload['parts']:
                file_name = payload['filename'].split('.')
                file_name = file_name[0] + " " + e['id']
                body = payload['body']
                file_path = f'{PDF_PATH}/{file_name}'
                if path.isfile(file_path) or 'extrato combinado' not in file_name.lower():
                    continue
                if 'attachmentId' in body:
                    att_id = body['attachmentId']

                    response = gmail_service.users().messages().attachments().get(
                        userId='me',
                        messageId=messageId,
                        id=att_id
                    ).execute()

                    file_data = base64.urlsafe_b64decode(
                        response.get('data').encode('UTF-8')
                    )
                    with open(file_path, 'wb') as fw:
                        fw.write(file_data)

if __name__ == '__main__':
    download_extratos()
