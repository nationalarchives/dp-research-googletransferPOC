import pandas as pd
import numpy as np
import os
import ast
import datetime


filelist = pd.read_csv('GoogleAPIMetadata.csv', converters={'google_parent_id': ast.literal_eval}, encoding="utf-8")
filelist = filelist.explode('google_parent_id')
filelist = filelist.drop_duplicates()
filelist = filelist.reset_index()
filelist['folder'] = ''
filelist['original_file_name'] = filelist['file_name']
filelist['file_name_note'] = ''
filelist['archivist_note'] = ''
filelist[''] = ''
content = {'identifier': ['content/'], 'file_name': ['content'], 'date_created': [datetime.datetime.now().isoformat()], 'date_last_modified': [datetime.datetime.now().isoformat()], 'folder':['folder']} #ading content folder in as this is the folder which it has been run form so does not get picked up by API
content = pd.DataFrame(content, columns = ['identifier','file_name','date_created','date_last_modified','folder'])

def replace_shortcuts():
    filelist['google_id'] = np.where(filelist.ShortcutID.isnull(), filelist['google_id'], filelist['ShortcutID'])
    filelist['mimeType'] = np.where(filelist.ShortcutID.isnull(), filelist['mimeType'], filelist['ShortcutMimeType'])
    filelist['date_created'] = np.where(filelist.ShortcutID.isnull(), filelist['date_created'], filelist['shortcutCreatedTime'])
    filelist['date_last_modified'] = np.where(filelist.ShortcutID.isnull(), filelist['date_last_modified'], filelist['shortcutModifiedTime'])

replace_shortcuts()

def get_parents(): #dictionary which takes list of google ID and parent ID, checks if parent ID is in list, adds to a parents list if so, then creates the idenrifier row with list of all parent IDs related to google ID
    parentslist = []
    filelist_dict = dict(zip(filelist.google_id, filelist.google_parent_id))
    for parent in filelist['google_parent_id']:
        T1 = ()
        while parent in filelist_dict.keys():
            for k, v in filelist_dict.items():
                if parent == k:
                        T1 = (k,) + T1
                        parent = v
        parentslist.append(T1)
    filelist['identifier'] = parentslist

get_parents()

def rename_googledocs(): #renames google docs with appropriate new filename for download, always leaves a note to state which format it is converting it to.
    filelist['file_name'] = np.where(filelist.mimeType == 'application/vnd.google-apps.document', filelist['file_name'] + '.gdoc.docx', filelist['file_name'])
    filelist['archivist_note'] = np.where(filelist.mimeType == 'application/vnd.google-apps.document', 'This file was originally a Google Doc format and has been converted to an Microsoft Office Word file', filelist['archivist_note'])
    filelist['file_name'] = np.where(filelist.mimeType == 'application/vnd.google-apps.spreadsheet', filelist['file_name'] + '.gsheet.xlsx', filelist['file_name'])
    filelist['archivist_note'] = np.where(filelist.mimeType == 'application/vnd.google-apps.spreadsheet', 'This file was originally a Google Sheets format and has been converted to an Microsoft Excel file', filelist['archivist_note'])
    filelist['file_name'] = np.where(filelist.mimeType == 'application/vnd.google-apps.presentation', filelist['file_name'] + '.gslide.pptx', filelist['file_name'])
    filelist['archivist_note'] = np.where(filelist.mimeType == 'application/vnd.google-apps.presentation', 'This file was originally a Google Slides format and has been converted to an Microsoft Powerpoint file', filelist['archivist_note'])
    filelist['file_name'] = np.where(filelist.mimeType == 'application/vnd.google-apps.drawing', filelist['file_name'] + '.gdraw.png', filelist['file_name'])
    filelist['archivist_note'] = np.where(filelist.mimeType == 'application/vnd.google-apps.drawing', 'This file was originally a Google Draw file and has been converted to a PNG file', filelist['archivist_note'])
    filelist['file_name'] = np.where(filelist.mimeType == 'application/vnd.google-apps.jam', filelist['file_name'] + '.gjamboard.pdf', filelist['file_name'])
    filelist['archivist_note'] = np.where(filelist.mimeType == 'application/vnd.google-apps.jam', 'This file was originally a Google Jamboard format and has been converted to a PDF file', filelist['archivist_note'])
rename_googledocs()

def rename_problem_files(): #renames caracters not allowed in file systems with, always leaves a note to say when filename has changed.
    filelist['file_name'] = filelist['file_name'].str.replace("/","_", regex=True)
    filelist['file_name'] = filelist['file_name'].str.replace("\\", "_", regex=True)
    filelist['file_name'] = filelist['file_name'].str.replace(":", "_", regex=True)
    filelist['file_name'] = filelist['file_name'].str.replace("*", "_", regex=True)
    filelist['file_name'] = filelist['file_name'].str.replace("?", "_", regex=True)
    filelist['file_name'] = filelist['file_name'].str.replace('"', '_', regex=True)
    filelist['file_name'] = filelist['file_name'].str.replace(">", "_", regex=True)
    filelist['file_name'] = filelist['file_name'].str.replace("<", "_", regex=True)
    filelist['file_name'] = filelist['file_name'].str.replace("|", "_", regex=True)
    filelist['file_name'] = filelist['file_name'].str.strip()
rename_problem_files()


def rename_duplicates(): #renames duplicate files with numerical number
    filelist['file_name'] = filelist['file_name'].astype(str)
    filesplit = pd.DataFrame([os.path.splitext(f) for f in filelist.file_name], columns=['Name', 'Ext'])
    filelist['file_name'] = filelist['file_name'].str.lower()
    c = filelist.groupby(["file_name", 'google_parent_id']).cumcount()
    c = c.astype(str)
    filelist['file_name'] = filesplit['Name'] + '(' + c + ')' + filesplit['Ext']
    filelist['file_name'] = filelist['file_name'].str.replace("\(0\)", "",regex = True)
    note_filesplit = pd.DataFrame([os.path.splitext(f) for f in filelist.file_name], columns=['Note_Name', 'Note_Ext'])
    original_filesplit = pd.DataFrame([os.path.splitext(f) for f in filelist.original_file_name], columns=['Original_Name', 'Original_Ext'])
    filelist['file_name_split'] = note_filesplit['Note_Name']
    filelist['original_file_name_split'] = original_filesplit['Original_Name']
    filelist['file_name_split'] = filelist['file_name_split'].str.replace(".gdoc","",regex = True)
    filelist['file_name_split'] = filelist['file_name_split'].str.replace(".gsheet", "",regex = True)
    filelist['file_name_split'] = filelist['file_name_split'].str.replace(".gslide", "",regex = True)
    filelist['file_name_split'] = filelist['file_name_split'].str.replace(".gdraw", "",regex = True)
    filelist['file_name_split'] = filelist['file_name_split'].str.replace(".gjamboard", "",regex = True)
    filelist['file_name_note'] = np.where(filelist.file_name_split != filelist.original_file_name_split,'This filename has been adjusted from the original', filelist['file_name_note'])
    print(filelist['file_name_split'])
    print(filelist['original_file_name_split'])
    del filelist['file_name_split']
    del filelist['original_file_name_split']
rename_duplicates()

def rename_folders(): #takes the identifier converts google id to file or folder name, then adds slashes, removes speech marks, creates folder column with folder or fie entries depending on mime type.

    filelist['identifier'] = filelist['identifier'].astype(str)
    mime = filelist.groupby('mimeType')
    foldernumbers = filelist['mimeType'].str.contains('application/vnd.google-apps.folder').sum()
    if foldernumbers>0:
        folders = mime.get_group('application/vnd.google-apps.folder')
        folder_dict =  dict(zip(folders.google_id, folders.file_name))

        for k, v in folder_dict.items():
            filelist['identifier'] = filelist['identifier'].str.replace(k,v)

    filelist['identifier'] = filelist['identifier'].str.lstrip("('").str.replace("'\)", '/', regex=True).str.replace("', '", "/", regex=True).str.replace("',\)", '/', regex=True).str.lstrip(')')
    filelist['identifier'] = filelist['identifier'] + filelist['file_name']
    filelist['identifier'] = np.where(filelist.mimeType == 'application/vnd.google-apps.folder', filelist['identifier'] + '/', filelist['identifier'])
    filelist['identifier'] = 'content/' + filelist['identifier']
    filelist['folder'] = np.where(filelist.mimeType == 'application/vnd.google-apps.folder', 'folder', filelist['folder'])
    filelist['folder'] = np.where(filelist.mimeType != 'application/vnd.google-apps.folder', 'file', filelist['folder'])

rename_folders()
content = pd.concat([content, filelist], sort=True)

def convert_to_tna(): #adds in TNA standard fields, converts date to xdatetime
    del content['index']
    content['closure_type'] = ''
    content['closure_period'] = ''
    content['closure_start_date'] = ''
    content['foi_exemption_code'] = ''
    content['foi_exemption_asserted'] = ''
    content['title_public'] = ''
    content['title_alternate'] = ''
    content['description_public'] = ''
    content['description_alternate'] = ''
    content['description'] = ''
    content['rights_copyright'] = 'Crown Copyright'
    content['legal_status'] = 'Public Record(s)'
    content['held_by'] = 'The National Archives, Kew'
    content['date_last_modified'] = pd.to_datetime(content["date_last_modified"])
    content['date_last_modified'] = content.date_last_modified.map(lambda x: datetime.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))
    content['date_created'] = pd.to_datetime(content["date_created"])
    content['date_created'] = content.date_created.map(lambda x: datetime.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))
    content['original_identifier'] = ''
    content['other_format_version_identifier'] = ''

convert_to_tna()

content = content.sort_values('identifier') #sorted by identifer (as DROID would do)
content = content[
        ['identifier', 'file_name','description','original_file_name', 'folder', 'date_created', 'date_last_modified','checksum_md5', 'closure_type',
         'closure_period', 'closure_start_date', 'foi_exemption_code', 'foi_exemption_asserted', 'title_public',
         'title_alternate','description_public','description_alternate', 'google_id', 'google_parent_id', 'rights_copyright', 'legal_status',
         'held_by', 'mimeType','size', 'archivist_note','file_name_note','original_identifier','other_format_version_identifier','standardDownloadLink','PDFDownloadLink']]
content.to_csv('GoogleTestMetadata.csv', index=False)
