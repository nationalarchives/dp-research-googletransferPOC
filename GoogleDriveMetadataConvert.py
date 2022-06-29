import pandas as pd
import numpy as np
import os
import ast
import datetime


filelist = pd.read_csv('GoogleAPIMetadata.csv', converters={'google_parent_id': ast.literal_eval})
filelist = filelist.explode('google_parent_id')
filelist = filelist.drop_duplicates()
filelist = filelist.reset_index()
filelist['folder'] = ''
filelist['original_file_name'] = filelist['file_name']
filelist['file_name_note'] = ''
filelist['archivist_note'] = ''
filelist[''] = ''
pdfcopy = ''
filelist2 = ''
content = {'identifier': ['content/'], 'file_name': ['content'], 'date_created': [datetime.datetime.now().isoformat()], 'date_last_modified': [datetime.datetime.now().isoformat()], 'folder':['folder']} #ading content folder in as this is the folder which it has been run form so does not get picked up by API
content = pd.DataFrame(content, columns = ['identifier','file_name','date_created','date_last_modified','folder'])

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

pdfcopy = filelist[filelist['mimeType'] == 'application/vnd.google-apps.document']
pdfcopy = pd.concat([pdfcopy, filelist[filelist['mimeType'] == 'application/vnd.google-apps.spreadsheet']])
pdfcopy = pd.concat([pdfcopy, filelist[filelist['mimeType'] == 'application/vnd.google-apps.presentation']])

def add_pdf_version(): #creates a sub dataframe to add a pdf version entry for all Google formats and renames with appropriate extension. This is then merged with the main dataframe
    pdfcopy['file_name'] = np.where(pdfcopy.mimeType == 'application/vnd.google-apps.document', pdfcopy['file_name'] + '.pdf', pdfcopy['file_name'])
    pdfcopy['archivist_note'] = np.where(pdfcopy.mimeType == 'application/vnd.google-apps.document', 'This file was originally a Google Doc format and has been converted to a PDF', pdfcopy['archivist_note'])
    pdfcopy['file_name'] = np.where(pdfcopy.mimeType == 'application/vnd.google-apps.spreadsheet', pdfcopy['file_name'] + '.pdf', pdfcopy['file_name'])
    pdfcopy['archivist_note'] = np.where(pdfcopy.mimeType == 'application/vnd.google-apps.spreadsheet', 'This file was originally a Google Sheets format and has been converted to a PDF', pdfcopy['archivist_note'])
    pdfcopy['file_name'] = np.where(pdfcopy.mimeType == 'application/vnd.google-apps.presentation', pdfcopy['file_name'] + '.pdf', pdfcopy['file_name'])
    pdfcopy['archivist_note'] = np.where(pdfcopy.mimeType == 'application/vnd.google-apps.presentation', 'This file was originally a Google Slides format and has been converted to a PDF', pdfcopy['archivist_note'])
    pdfcopy['mimeType'] = 'application/pdf'
add_pdf_version()

def rename_googledocs(): #renames google docs with appropriate new filname for download, always leaves a note to state which format it is converting it to.
    filelist['file_name'] = np.where(filelist.mimeType == 'application/vnd.google-apps.document', filelist['file_name'] + '.docx', filelist['file_name'])
    filelist['archivist_note'] = np.where(filelist.mimeType == 'application/vnd.google-apps.document', 'This file was originally a Google Doc format and has been converted to an Microsoft Office Word file', filelist['archivist_note'])
    filelist['file_name'] = np.where(filelist.mimeType == 'application/vnd.google-apps.spreadsheet', filelist['file_name'] + '.xlsx', filelist['file_name'])
    filelist['archivist_note'] = np.where(filelist.mimeType == 'application/vnd.google-apps.spreadsheet', 'This file was originally a Google Sheets format and has been converted to an Microsoft Excel file', filelist['archivist_note'])
    filelist['file_name'] = np.where(filelist.mimeType == 'application/vnd.google-apps.presentation', filelist['file_name'] + '.pptx', filelist['file_name'])
    filelist['archivist_note'] = np.where(filelist.mimeType == 'application/vnd.google-apps.presentation', 'This file was originally a Google Slides format and has been converted to an Microsoft Powerpoint file', filelist['archivist_note'])
    filelist['file_name'] = np.where(filelist.mimeType == 'application/vnd.google-apps.drawing', filelist['file_name'] + '.png', filelist['file_name'])
    filelist['archivist_note'] = np.where(filelist.mimeType == 'application/vnd.google-apps.drawing', 'This file was originally a Google Draw file and has been converted to a PNG file', filelist['archivist_note'])
    filelist['file_name'] = np.where(filelist.mimeType == 'application/vnd.google-apps.jam', filelist['file_name'] + '.pdf', filelist['file_name'])
    filelist['archivist_note'] = np.where(filelist.mimeType == 'application/vnd.google-apps.jam', 'This file was originally a Google Jamboard format and has been converted to a PDF file', filelist['archivist_note'])
rename_googledocs()

filelist2 = pd.concat([filelist, pdfcopy], ignore_index=True)


def rename_problem_files(): #renames caracters not allowed in file systems with, always leaves a note to say when filename has changed.
    filelist2['file_name'] = filelist2['file_name'].str.replace("/","_", regex=True)
    filelist2['file_name'] = filelist2['file_name'].str.replace("\\", "_", regex=True)
    filelist2['file_name'] = filelist2['file_name'].str.replace(":", "_", regex=True)
    filelist2['file_name'] = filelist2['file_name'].str.replace("*", "_", regex=True)
    filelist2['file_name'] = filelist2['file_name'].str.replace("?", "_", regex=True)
    filelist2['file_name'] = filelist2['file_name'].str.replace('"', '_', regex=True)
    filelist2['file_name'] = filelist2['file_name'].str.replace(">", "_", regex=True)
    filelist2['file_name'] = filelist2['file_name'].str.replace("<", "_", regex=True)
    filelist2['file_name'] = filelist2['file_name'].str.replace("|", "_", regex=True)
rename_problem_files()


def rename_duplicates(): #renames duplicate files with numerical number
    filelist2.to_csv('pdfcheck.csv', index=False)
    filelist2['file_name'] = filelist2['file_name'].astype(str)
    filesplit = pd.DataFrame([os.path.splitext(f) for f in filelist2.file_name],columns=['Name','Ext'])
    c = filelist2.groupby(["file_name",'google_parent_id']).cumcount()
    c = c.astype(str)
    filelist2['file_name'] = filesplit['Name'] + '(' + c + ')' + filesplit['Ext']
    filelist2['file_name'] = filelist2['file_name'].str.replace("\(0\)","", regex = True)
    filelist2['file_name_note'] = np.where(filelist2.file_name != filelist2.original_file_name,'This filename has been adjusted from the original: '+filelist2.original_file_name,filelist2['file_name_note'])
    filelist2['file_name_note'] = np.where((filelist2.file_name == filelist2.original_file_name+'.xlsx') | (filelist2.file_name == filelist2.original_file_name + '.docx') | (filelist2.file_name == filelist2.original_file_name + '.pptx') | (filelist2.file_name == filelist2.original_file_name + '.png') | (filelist2.file_name == filelist2.original_file_name + '.pdf'),'',filelist2['file_name_note'])
rename_duplicates()

def rename_folders(): #takes the identifier converts google id to file or folder name, then adds slashes, removes speech marks, creates folder column with folder or fie entries depending on mime type.

    filelist2['identifier'] = filelist2['identifier'].astype(str)
    mime = filelist2.groupby('mimeType')
    foldernumbers = filelist2['mimeType'].str.contains('application/vnd.google-apps.folder').sum()
    if foldernumbers>0:
        folders = mime.get_group('application/vnd.google-apps.folder')
        folder_dict =  dict(zip(folders.google_id, folders.file_name))

        for k, v in folder_dict.items():
            filelist2['identifier'] = filelist2['identifier'].str.replace(k,v)

    filelist2['identifier'] = filelist2['identifier'].str.lstrip("('").str.replace("'\)",'/', regex=True).str.replace("', '","/", regex=True).str.replace("',\)",'/', regex=True).str.lstrip(')')
    filelist2['identifier'] = filelist2['identifier'] + filelist2['file_name']
    filelist2['identifier'] = np.where(filelist2.mimeType == 'application/vnd.google-apps.folder', filelist2['identifier'] + '/', filelist2['identifier'])
    filelist2['identifier'] = 'content/' + filelist2['identifier']
    filelist2['folder'] = np.where(filelist2.mimeType == 'application/vnd.google-apps.folder', 'folder', filelist2['folder'])
    filelist2['folder'] = np.where(filelist2.mimeType != 'application/vnd.google-apps.folder', 'file', filelist2['folder'])

rename_folders()
content = pd.concat([content, filelist2], sort=True)

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
    content['other_format_version_identifier'] = np.where(content.archivist_note == 'This file was originally a Google Doc format and has been converted to a PDF', content['identifier'].str.replace(".pdf$",'.docx', regex=True), content['other_format_version_identifier'])
    content['other_format_version_identifier'] = np.where(content.archivist_note == 'This file was originally a Google Sheets format and has been converted to a PDF', content['identifier'].str.replace(".pdf$",'.xlsx', regex=True), content['other_format_version_identifier'])
    content['other_format_version_identifier'] = np.where(content.archivist_note == 'This file was originally a Google Slides format and has been converted to a PDF', content['identifier'].str.replace(".pdf$",'.pptx', regex=True), content['other_format_version_identifier'])
convert_to_tna()

content = content.sort_values('identifier') #sorted by identifer (as DROID would do)
content = content[
        ['identifier', 'file_name','description','original_file_name', 'folder', 'date_created', 'date_last_modified','checksum_md5', 'closure_type',
         'closure_period', 'closure_start_date', 'foi_exemption_code', 'foi_exemption_asserted', 'title_public',
         'title_alternate','description_public','description_alternate', 'google_id', 'google_parent_id', 'rights_copyright', 'legal_status',
         'held_by', 'mimeType','size', 'archivist_note','file_name_note','original_identifier', 'other_format_version_identifier']]
content.to_csv('GoogleTestMetadata.csv', index=False)

