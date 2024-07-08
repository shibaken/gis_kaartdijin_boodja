import sys
import os
from utils import (
    fetch_file_list,
    retrieve_file_content,
    delete_file_remotely,
    read_config_json,
    create_folder,
    save_file_locally
)

# Start this script
print('Starting the script...')

# Open config file
config_data = read_config_json()

# Create local distination folder
create_folder(config_data['DESTINATION_FOLDER'])

# Fetch file info
response = fetch_file_list(config_data['ENDPOINT_URL'], config_data['USERNAME'], config_data['PASSWORD'])
print(response)
total_files = response['count']

if not total_files:
    print('No files found.')
    sys.exit(0)

# Print total number of files
print(f'Total number of files: {total_files}')

count = 0
for file_info in response['results']:
    count += 1
    print(f"--- File#{count} (out of {total_files}) files ---")

    # Retrieve file contents
    file_content = retrieve_file_content(config_data['ENDPOINT_URL'], config_data['USERNAME'], config_data['PASSWORD'], file_info['filepath'])
    if file_content:
        # Save file contents locally
        save_file_locally(file_content, file_info['filepath'], config_data['DESTINATION_FOLDER'])
        # Destroy file from the server
        delete_file_remotely(config_data['ENDPOINT_URL'], config_data['USERNAME'], config_data['PASSWORD'], file_info['filepath'])
