#!/usr/bin/python3

"""

  In order to run this script you need python3 and pip3 installed.

  You also need some additional python modules. Please run

    sudo pip3 install httplib2

    sudo pip3 install --upgrade google-api-python-client



  To authenticate in Google follow the instructions at

  https://developers.google.com/drive/v3/web/quickstart/python

  A client_secret.json file needs to placed in the same directory

  with this script. The link above contains the instruction on

  how to obtain this file. Once you complete these steps run

    python3 this_script.py --noauth_local_webserver

  and follow the instructions

"""

import httplib2

import os

import shutil

from apiclient import discovery

from oauth2client import client

from oauth2client import tools

from oauth2client.file import Storage

from datetime import datetime

try:

    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

except ImportError:

    flags = None

import csv
series = 'TEST_1'
batch = 'TEST1Y22HB001'
validatePath = 'Downloads/'+datetime.today().strftime('%Y-%m-%d-%H_%M_%S')+'/' + batch + '/'
downloadArea =  validatePath + series + '/'
downloadPath = '\\\\?\\' + downloadArea.replace('/','\\')
schema = "GoogleSchema.csvs"
closureSchema = "closure_v13.csvs"
closureMetadata = 'closure_v13.csv'
finalMetadata = 'metadata_GoogleSchema_'+batch+'.csv'
downloadfinalMetadata = downloadArea+'/'+finalMetadata
metadata = 'GoogleTestMetadata.csv'
logfile = open("logfile"+datetime.today().strftime('%Y-%m-%d-%H_%M_%S')+".txt", "w+")
wd = os.getcwd()

import io
from io import BytesIO
from googleapiclient.http import MediaIoBaseDownload
import datetime
from datetime import date
import os
import hashlib
import pandas as pd
import numpy as np
import urllib.parse
import subprocess
import requests


# If modifying these scopes, delete your previously saved credentials

# at ~/.credentials/drive-python-quickstart.json

SCOPES = 'https://www.googleapis.com/auth/drive.readonly'

CLIENT_SECRET_FILE = 'credentials2.json'

APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.



    If nothing has been stored, or if the stored credentials are invalid,

    the OAuth2 flow is completed to obtain the new credentials.



    Returns:

        Credentials, the obtained credential.

    """

    home_dir = os.path.expanduser('~')

    credential_dir = os.path.join(home_dir, '.credentials2')

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    credential_path = os.path.join(credential_dir,

                                   'drive-python-quickstart.json')

    store = Storage(credential_path)

    credentials = store.get()

    if not credentials or credentials.invalid:

        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)

        flow.user_agent = APPLICATION_NAME

        if flags:

            credentials = tools.run_flow(flow, store, flags)

        else:  # Needed only for compatibility with Python 2.6

            credentials = tools.run(flow, store)

        print('Storing credentials to ' + credential_path)

    return credentials


def downloadFileList(): #using metadata file to recreate file structure of folders, and download files using api requests based on google id. Picks up mimetype of files, if google cloud formats converts to open office equivalant, if anything else downloads as is
    credentials = get_credentials()

    http = credentials.authorize(httplib2.Http())

    service = discovery.build('drive', 'v3', http=http)
    with open(metadata, 'rt', encoding='utf8') as f:
        next(f)
        next(f)
        reader = csv.reader(f)
        for row in reader:
            mimeType = row[22]
            ID = row[17]
            filepath = row[0]
            filepath = filepath.replace("/", "\\")
            note = row[24]
            if mimeType == 'application/vnd.google-apps.folder':
                try:
                    os.makedirs(downloadPath + filepath)
                except:
                    pass

            elif mimeType == 'application/vnd.google-apps.document':
                try:
                    request = service.files().export_media(fileId=ID,
                                                       mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    fh = io.FileIO(downloadPath + filepath, 'wb')
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print ("Download %d%%." % int(status.progress() * 100))
                except:
                    try:
                        OSError
                        directory = os.path.dirname(filepath)
                        os.makedirs(downloadPath + directory)
                        request = service.files().export_media(fileId=ID,
                                                               mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                        fh = io.FileIO(downloadPath + filepath, 'wb')
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print ("Download %d%%." % int(status.progress() * 100))
                    except:
                        try:
                            headers = {'Authorization': 'Bearer {}'.format(credentials.access_token), 'User-Agent': 'Mozilla/5.0'}
                            request = "https://docs.google.com/document/d/" + ID + '/export?format=docx'
                            response = requests.get(request, headers=headers)
                            open(downloadPath + filepath, 'wb').write(response.content)
                        except:
                            print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID)
                            print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID, file=logfile)
                            pass
            elif mimeType == 'application/vnd.google-apps.spreadsheet':
                try:
                    request = service.files().export_media(fileId=ID,
                                                           mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    fh = io.FileIO(downloadPath + filepath, 'wb')
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print("Download %d%%." % int(status.progress() * 100))
                except:
                    try:
                        OSError
                        directory = os.path.dirname(filepath)
                        os.makedirs(downloadPath + directory)
                        request = service.files().export_media(fileId=ID,
                                                               mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                        fh = io.FileIO(downloadPath + filepath, 'wb')
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print("Download %d%%." % int(status.progress() * 100))
                    except:
                        try:
                            headers = {'Authorization': 'Bearer {}'.format(credentials.access_token),
                                           'User-Agent': 'Mozilla/5.0'}
                            request = "https://docs.google.com/spreadsheets/d/" + ID + '/export?format=xlsx'
                            response = requests.get(request, headers=headers)
                            open(downloadPath + filepath, 'wb').write(response.content)
                        except:
                            print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID)
                            print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID, file=logfile)
                            pass
            elif mimeType == 'application/vnd.google-apps.presentation':
                try:
                    request = service.files().export_media(fileId=ID,
                                                           mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation')
                    fh = io.FileIO(downloadPath + filepath, 'wb')
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print("Download %d%%." % int(status.progress() * 100))
                except:
                    try:
                        OSError
                        directory = os.path.dirname(filepath)
                        os.makedirs(downloadPath + directory)
                        request = service.files().export_media(fileId=ID,
                                                               mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation')
                        fh = io.FileIO(downloadPath + filepath, 'wb')
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print("Download %d%%." % int(status.progress() * 100))
                    except:
                        try:
                            headers = {'Authorization': 'Bearer {}'.format(credentials.access_token),
                                       'User-Agent': 'Mozilla/5.0'}
                            request = "https://docs.google.com/presentation/d/"+ID+'/export/pptx'
                            response = requests.get(request, headers=headers)
                            open(downloadPath + filepath, 'wb').write(response.content)
                        except:
                            print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID)
                            print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID, file=logfile)
                            pass
            elif mimeType == 'application/vnd.google-apps.drawing':
                try:
                    request = service.files().export_media(fileId=ID,
                                                           mimeType='image/png')
                    fh = io.FileIO(downloadPath + filepath, 'wb')
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print("Download %d%%." % int(status.progress() * 100))
                except:
                    OSError
                    try:
                        directory = os.path.dirname(filepath)
                        os.makedirs(downloadPath + directory)
                        request = service.files().export_media(fileId=ID,
                                                           mimeType='image/png')
                        fh = io.FileIO(downloadPath + filepath, 'wb')
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print("Download %d%%." % int(status.progress() * 100))
                    except:
                        try:
                            headers = {'Authorization': 'Bearer {}'.format(credentials.access_token),
                                           'User-Agent': 'Mozilla/5.0'}
                            request = "https://docs.google.com/drawings/d/" + ID + '/export/png'
                            response = requests.get(request, headers=headers)
                            open(downloadPath + filepath, 'wb').write(response.content)
                        except:
                            print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID)
                            print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID, file=logfile)
                            pass
            elif mimeType == 'application/vnd.google-apps.jam':
                try:
                    request = service.files().export_media(fileId=ID,
                                                           mimeType='application/pdf')
                    fh = io.FileIO(downloadPath + filepath, 'wb')
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print("Download %d%%." % int(status.progress() * 100))
                except:
                    OSError
                    try:
                        directory = os.path.dirname(filepath)
                        os.makedirs(downloadPath + directory)
                        request = service.files().export_media(fileId=ID,
                                                               mimeType='application/pdf')
                        fh = io.FileIO(downloadPath + filepath, 'wb')
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print("Download %d%%." % int(status.progress() * 100))
                    except:
                        try:
                            headers = {'Authorization': 'Bearer {}'.format(credentials.access_token),
                                       'User-Agent': 'Mozilla/5.0'}
                            request = "https://jamboard.google.com/d/" + ID + '/export?format=pdf'
                            response = requests.get(request, headers=headers)
                            open(downloadPath + filepath, 'wb').write(response.content)
                        except:
                            print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID)
                            print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID, file=logfile)
                            pass
            elif mimeType == 'application/pdf':
                if note == 'This file was originally a Google Doc format and has been converted to a PDF':
                    try:
                        request = service.files().export_media(fileId=ID,
                                                       mimeType='application/pdf')
                        fh = io.FileIO(downloadPath + filepath, 'wb')
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print ("Download %d%%." % int(status.progress() * 100))
                    except:
                        try:
                            OSError
                            directory = os.path.dirname(filepath)
                            os.makedirs(downloadPath + directory)
                            request = service.files().export_media(fileId=ID,
                                                               mimeType='application/pdf')
                            fh = io.FileIO(downloadPath + filepath, 'wb')
                            downloader = MediaIoBaseDownload(fh, request)
                            done = False
                            while done is False:
                                status, done = downloader.next_chunk()
                                print ("Download %d%%." % int(status.progress() * 100))
                        except:
                            try:
                                headers = {'Authorization': 'Bearer {}'.format(credentials.access_token), 'User-Agent': 'Mozilla/5.0'}
                                request = "https://docs.google.com/document/d/" + ID + '/export?format=pdf'
                                response = requests.get(request, headers=headers)
                                open(downloadPath + filepath, 'wb').write(response.content)
                            except:
                                print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID)
                                print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID, file=logfile)
                                pass
                elif note == 'This file was originally a Google Sheets format and has been converted to a PDF':
                    try:
                        request = service.files().export_media(fileId=ID,
                                              mimeType='application/pdf')
                        fh = io.FileIO(downloadPath + filepath, 'wb')
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print("Download %d%%." % int(status.progress() * 100))
                    except:
                        try:
                            OSError
                            directory = os.path.dirname(filepath)
                            os.makedirs(downloadPath + directory)
                            request = service.files().export_media(fileId=ID,
                                                 mimeType='application/pdf')
                            fh = io.FileIO(downloadPath + filepath, 'wb')
                            downloader = MediaIoBaseDownload(fh, request)
                            done = False
                            while done is False:
                                status, done = downloader.next_chunk()
                                print("Download %d%%." % int(status.progress() * 100))
                        except:
                            try:
                                headers = {'Authorization': 'Bearer {}'.format(credentials.access_token), 'User-Agent': 'Mozilla/5.0'}
                                request = "https://docs.google.com/spreadsheets/d/" + ID + '/export?format=pdf'
                                response = requests.get(request, headers=headers)
                                open(downloadPath + filepath, 'wb').write(response.content)
                            except:
                                print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID)
                                print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID, file=logfile)
                                pass
                elif note == 'This file was originally a Google Slides format and has been converted to a PDF':
                    try:
                        request = service.files().export_media(fileId=ID,
                                              mimeType='application/pdf')
                        fh = io.FileIO(downloadPath + filepath, 'wb')
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print("Download %d%%." % int(status.progress() * 100))
                    except:
                        try:
                            OSError
                            directory = os.path.dirname(filepath)
                            os.makedirs(downloadPath + directory)
                            request = service.files().export_media(fileId=ID,
                                                 mimeType='application/pdf')
                            fh = io.FileIO(downloadPath + filepath, 'wb')
                            downloader = MediaIoBaseDownload(fh, request)
                            done = False
                            while done is False:
                                status, done = downloader.next_chunk()
                                print("Download %d%%." % int(status.progress() * 100))
                        except:
                            try:
                                headers = {'Authorization': 'Bearer {}'.format(credentials.access_token), 'User-Agent': 'Mozilla/5.0'}
                                request = "https://docs.google.com/presentation/d/"+ID+'/export/pdf'
                                response = requests.get(request, headers=headers)
                                open(downloadPath + filepath, 'wb').write(response.content)
                            except:
                                print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID)
                                print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID, file=logfile)
                                pass
                else:
                    try:
                        request = service.files().get_media(fileId=ID)
                        fh = io.FileIO(downloadPath + filepath, 'wb')
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print("Download %d%%." % int(status.progress() * 100))
                    except:
                        OSError
                        try:
                            directory = os.path.dirname(filepath)
                            os.makedirs(downloadPath + directory)
                            request = service.files().get_media(fileId=ID)
                            fh = io.FileIO(downloadPath + filepath, 'wb')
                            downloader = MediaIoBaseDownload(fh, request)
                            done = False
                            while done is False:
                                status, done = downloader.next_chunk()
                                print("Download %d%%." % int(status.progress() * 100))
                        except:
                            try:
                                request = service.files().get_media(fileId=ID)
                                fh = io.FileIO(downloadPath + filepath, 'wb')
                                downloader = MediaIoBaseDownload(fh, request)
                                done = False
                                while done is False:
                                    status, done = downloader.next_chunk()
                                    print("Download %d%%." % int(status.progress() * 100))
                            except Exception as e:
                                print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID)
                                print(e)
                                print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID, file=logfile)
                                pass
            else:
                try:
                    request = service.files().get_media(fileId=ID)
                    fh = io.FileIO(downloadPath + filepath, 'wb')
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print("Download %d%%." % int(status.progress() * 100))
                except:
                    OSError
                    try:
                        directory = os.path.dirname(filepath)
                        os.makedirs(downloadPath + directory)
                        request = service.files().get_media(fileId=ID)
                        fh = io.FileIO(downloadPath + filepath, 'wb')
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print("Download %d%%." % int(status.progress() * 100))
                    except:
                        try:
                            request = service.files().get_media(fileId=ID)
                            fh = io.FileIO(downloadPath + filepath, 'wb')
                            downloader = MediaIoBaseDownload(fh, request)
                            done = False
                            while done is False:
                                status, done = downloader.next_chunk()
                                print("Download %d%%." % int(status.progress() * 100))
                        except Exception as e:
                            print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID)
                            print(e)
                            print('Issue downloading ' + filepath + ' file has not been downloaded, Google ID: ' + ID, file=logfile)
                            pass
            print('Downloading', reader.line_num)

downloadFileList()
print('Files Downloaded')
print('Generating SHA256')

def encode(identifier): #converts identifier encoding to URI
    identifier = urllib.parse.quote(identifier)
    return identifier

def encode_redacted(original_identifier): #converts identifier encoding to URI
    original_identifier = urllib.parse.quote(str(original_identifier))
    return original_identifier

def encode_other_format(other_format_version_identifier): #converts identifier encoding to URI
    other_format_version_identifier = urllib.parse.quote(str(other_format_version_identifier))
    return other_format_version_identifier

sha256=[]


def tidy_metadata(): #finishes of the rest of actions needed, generates sha256, runs encode to convert identifiers to URI, removes unneeded columns, edits identifier filepath to match TNA requirements, splits metadata and closure metadata
    with open(metadata, 'rt', encoding='utf8') as f:
        next(f)
        reader = csv.reader(f)
        for row in reader:
            folder = row[4]
            identifier = row[0]
            identifier2 = identifier.replace('/', '\\')
            if folder == 'file':
                with open(downloadPath + identifier2, 'rb') as afile:
                    print('reading file',identifier2)
                    sha256_object = hashlib.sha256()
                    block_size = 65536 * sha256_object.block_size
                    chunk = afile.read(block_size)
                    while chunk:
                        sha256_object.update(chunk)
                        chunk = afile.read(block_size)
                    gethash = sha256_object.hexdigest()
                    sha256.append(gethash)
            else:
                sha256.append('None')
    filelist = pd.read_csv(metadata, encoding='utf8')
    filelist['identifier'] = filelist.identifier.apply(encode)
    filelist['identifier'] = 'file:/' + series + '/' + filelist['identifier']
    filelist['title_public'] = filelist['title_public'].astype(str)
    filelist['title_public'] = np.where(filelist['title_public'] == 'True', 'TRUE', filelist['title_public'])
    filelist['description_public'] = filelist['title_public'].astype(str)
    filelist['description_public'] = np.where(filelist['description_public'] == 'True', 'TRUE', filelist['description_public'])
    filelist['original_identifier'] = filelist.original_identifier.apply(encode_redacted)
    try:
        filelist['original_identifier'] = np.where(~filelist['original_identifier'].isnull(),'file:/' + series + '/' + filelist['original_identifier'], filelist['original_identifier'])
    except:
        pass
    filelist['original_identifier'] = np.where(filelist['original_identifier'] == 'file:/' + series + '/' + 'nan', '', filelist['original_identifier'])
    filelist['other_format_version_identifier'] = filelist.other_format_version_identifier.apply(encode_other_format)
    try:
        filelist['other_format_version_identifier'] = np.where(~filelist['other_format_version_identifier'].isnull(), 'file:/' + series + '/' + filelist['other_format_version_identifier'], filelist['other_format_version_identifier'])
    except:
        pass
    filelist['other_format_version_identifier'] = np.where(filelist['other_format_version_identifier'] == 'file:/' + series + '/' + 'nan', '', filelist['other_format_version_identifier'])
    closure = filelist[['identifier','folder','closure_type','closure_period','closure_start_date','foi_exemption_code','foi_exemption_asserted','title_public','title_alternate','description_public','description_alternate']]
    try:
        filelist['archivist_note'] = np.where(~filelist['file_name_note'].isnull(), filelist['archivist_note'] + '. ' + filelist['file_name_note'], filelist['archivist_note'])
    except:
        pass
    try:
        filelist['archivist_note'] = np.where((~filelist['file_name_note'].isnull()) & (filelist['archivist_note'].isnull()), filelist['file_name_note'], filelist['archivist_note'])
    except:
        pass
    del filelist['mimeType']
    del filelist['size']
    del filelist['original_file_name']
    del filelist['file_name_note']
    del filelist['closure_type']
    del filelist['closure_period']
    del filelist['closure_start_date']
    del filelist['foi_exemption_code']
    del filelist['foi_exemption_asserted']
    del filelist['title_public']
    del filelist['title_alternate']
    del filelist['description_public']
    del filelist['description_alternate']
    filelist['checksum'] = sha256
    filelist['checksum'] = np.where(filelist.checksum == 'None', '', filelist['checksum'])
    filelist['date_archivist_note'] = ''
    filelist['date_archivist_note'] = np.where(~filelist['archivist_note'].isnull(), datetime.datetime.today().strftime('%d/%m/%Y'),filelist['date_archivist_note'])

    filelist = filelist[
        ['identifier', 'file_name', 'folder','description', 'date_created','end_date', 'date_last_modified', 'checksum_md5', 'checksum', 'google_id', 'google_parent_id', 'rights_copyright', 'legal_status',
         'held_by','note','archivist_note','date_archivist_note','original_identifier','other_format_version_identifier']]
    filelist.to_csv(downloadfinalMetadata, index=False)
    closure.to_csv(downloadPath+closureMetadata, index=False)
tidy_metadata()



print('Validating metadata')
subprocess.run(["csv-validator-cmd-1.2-RC2-application\\csv-validator-cmd-1.2-RC2\\bin\\validate.bat", downloadfinalMetadata, schema, "-p:file:/=file:/"+validatePath], shell=True)
print('Validating closure metadata')
subprocess.run(["csv-validator-cmd-1.2-RC2-application\\csv-validator-cmd-1.2-RC2\\bin\\validate.bat", downloadArea+closureMetadata, closureSchema, "-p:file:/=file:/"+validatePath], shell=True)
print('Generating metadata hash')
with open(downloadfinalMetadata, 'rb') as afile:
    hash = afile.read()
    gethash = hashlib.sha256(hash).hexdigest()
    f = open(downloadfinalMetadata+".sha256", "w", newline='\n')
    f.write(gethash+ "  " +finalMetadata+'\n')
with open(downloadPath+closureMetadata, 'rb') as afile:
    hash = afile.read()
    gethash = hashlib.sha256(hash).hexdigest()
    f = open(downloadPath+closureSchema+".sha256", "w", newline='\n')
    f.write(gethash+ "  " +closureMetadata+'\n')
shutil.copyfile(schema, downloadArea+schema)
shutil.copyfile(closureSchema, downloadArea+closureSchema)
print('done!')
