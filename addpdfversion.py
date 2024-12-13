import pandas as pd
import numpy as np

filelist = pd.read_csv('GoogleTestMetadata.csv', encoding='utf8')
filelist['other_format_version_identifier'] = ''
pdfcopy = filelist[filelist['mimeType'] == 'application/vnd.google-apps.document']
pdfcopy = pd.concat([pdfcopy, filelist[filelist['mimeType'] == 'application/vnd.google-apps.spreadsheet']])
pdfcopy = pd.concat([pdfcopy, filelist[filelist['mimeType'] == 'application/vnd.google-apps.presentation']])
content = ''

def add_pdf_version(): #creates a sub dataframe to add a pdf version entry for all Google formats and renames with appropriate extension. This is then merged with the main dataframe
    pdfcopy['file_name'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Doc format and has been converted to an Microsoft Office Word file', pdfcopy['file_name'].str.replace('docx$', 'pdf', regex=True), pdfcopy['file_name'])
    pdfcopy['archivist_note'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Doc format and has been converted to an Microsoft Office Word file', 'This file was originally a Google Doc format and has been converted to a PDF', pdfcopy['archivist_note'])
    pdfcopy['identifier'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Doc format and has been converted to an Microsoft Office Word file', pdfcopy['identifier'].str.replace('docx$', 'pdf', regex=True), pdfcopy['identifier'])
    pdfcopy['file_name'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Sheets format and has been converted to an Microsoft Excel file', pdfcopy['file_name'].str.replace('xlsx$', 'pdf', regex=True), pdfcopy['file_name'])
    pdfcopy['archivist_note'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Sheets format and has been converted to an Microsoft Excel file', 'This file was originally a Google Sheets format and has been converted to a PDF', pdfcopy['archivist_note'])
    pdfcopy['identifier'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Doc format and has been converted to an Microsoft Office Excel file', pdfcopy['identifier'].str.replace('xslx$', 'pdf', regex=True), pdfcopy['identifier'])
    pdfcopy['file_name'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Slides format and has been converted to an Microsoft Powerpoint file', pdfcopy['file_name'].str.replace('pptx$', 'pdf', regex=True), pdfcopy['file_name'])
    pdfcopy['archivist_note'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Slides format and has been converted to an Microsoft Powerpoint file', 'This file was originally a Google Slides format and has been converted to a PDF', pdfcopy['archivist_note'])
    pdfcopy['identifier'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Doc format and has been converted to an Microsoft Office Powerpoint file', pdfcopy['identifier'].str.replace('pptx$', 'pdf', regex=True), pdfcopy['identifier'])
    pdfcopy['identifier'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Doc format and has been converted to a PDF',pdfcopy['identifier'].str.replace("docx$", 'pdf', regex=True), pdfcopy['identifier'])
    pdfcopy['identifier'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Sheets format and has been converted to a PDF',pdfcopy['identifier'].str.replace("xlsx$", 'pdf', regex=True), pdfcopy['identifier'])
    pdfcopy['identifier'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Slides format and has been converted to a PDF',pdfcopy['identifier'].str.replace("pptx$", 'pdf', regex=True), pdfcopy['identifier'])
    pdfcopy['mimeType'] = 'application/pdf'
add_pdf_version()


def add_other_format_identifier():
    pdfcopy['other_format_version_identifier'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Doc format and has been converted to a PDF', pdfcopy['identifier'].str.replace(".pdf$", '.docx', regex=True), pdfcopy['other_format_version_identifier'])
    pdfcopy['other_format_version_identifier'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Sheets format and has been converted to a PDF', pdfcopy['identifier'].str.replace(".pdf$", '.xlsx', regex=True), pdfcopy['other_format_version_identifier'])
    pdfcopy['other_format_version_identifier'] = np.where(pdfcopy.archivist_note == 'This file was originally a Google Slides format and has been converted to a PDF', pdfcopy['identifier'].str.replace(".pdf$", '.pptx', regex=True), pdfcopy['other_format_version_identifier'])
add_other_format_identifier()

content = pd.concat([filelist, pdfcopy], ignore_index=True)

content = content.sort_values('identifier')  # sorted by identifer (as DROID would do)
content = content[
        ['identifier', 'file_name', 'description', 'original_file_name', 'folder', 'date_created', 'date_last_modified','end_date',
         'checksum_md5', 'closure_type',
         'closure_period', 'closure_start_date', 'foi_exemption_code', 'foi_exemption_asserted', 'title_public',
         'title_alternate', 'description_public', 'description_alternate', 'google_id', 'google_parent_id',
         'rights_copyright', 'legal_status',
         'held_by', 'mimeType', 'size','note', 'archivist_note', 'file_name_note', 'original_identifier',
         'other_format_version_identifier']]
content.to_csv('GoogleTestMetadataPDF.csv', index=False)
