# dp-research-googletransferPOC
POC scripts to test potential transfer processes for material to TNA stored in Google Drive.

Scripts are authenticated using Python Quickstart example from Google - https://developers.google.com/drive/v3/web/quickstart/python to set up you will need to follow the authentication steps detailed there and download a json file with the access credentials. This needs to be renamed 'credentials.json' and placed in the same place as these scripts are run.

On first run both the scripts googleApiFileList.py and googleDownload.py will ask for a Google account (which has access to the relevant files) to give access to the script. The script will state the scope it needs to run. GoogleApiFileList.py will ask for read only access to the metadata of files. GoogleDownload.py requires read only access to files and metadata.

1. Initial script GoogleApiFileList generates a folder and file list of all folders under a specified Google folder ID. To get the ID of the folder you want to scan you can go into Google Drive and copy the folder ID from the end of the URI. You can edit the folder_id variable in the script with your relevant google ID. This script will output a file called GoogleAPIMetadata.csv.

2. GoogleDriveMetadata take the output GoogleAPIMetadata.csv and starts to convert it to the TNA template. This includes the following steps.

- It will add in closure metadata columns and standard TNA fields. E.g. Copyright, legal status
- adds a 'content' folder as the highest directory level
- reconstructs the filepath using id and parent ids
- renames google docs with the extensions of their export formats, adds a 'archivist_note' column which details actions taken
- renames problem characters /\:\*?"<>| with an _ 
- renames duplicate file and folder names in the same directory, adds an incremental number

It retains some fields such as mimeType, which will not be retained in the final CSV, as these are used in the GoogleDownload script.

3. The third script googleDownload, downloads files in their original folder structure. Non-Google formats are downloaded in their original formats. Google formats are downloaded in specified export formats (generally open office). 

Final metadata changes are then completed, fields which are not needed are removed. Additional SHA256 checksums are generated and validation is achieved using the CSV validator https://github.com/digital-preservation/csv-validator and schemas GoogleSchema.csvs and closure_v6.csvs (currently closure schema validation rules are commented out as closure is not completed in this process).

