import os
import sys
import json
import requests


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An error occurred: {e}")
    return wrapper


def read_config_json(filename='config.ini'):
    """
    Read JSON data directly from a config.ini file located in the same folder as the script.
    Args: filename (str): Name of the config file. Default is 'config.ini'.
    Returns: dict: JSON data read from the config file.
    """
    # Get the absolute path to the config file
    config_path = os.path.join(os.path.dirname(__file__), filename)

    # Check if the config file exists
    if not os.path.exists(config_path):
        print(f"Config file '{filename}' not found at path: {config_path}")
        raise FileNotFoundError(f"Config file '{filename}' not found.")

    print(f"Reading JSON data from config file: {config_path}")

    # Read the JSON data from the config file
    with open(config_path, 'r') as file:
        json_data = json.load(file)

    print("JSON data read successfully.")

    # Return the JSON data
    return json_data


@handle_exceptions
def fetch_file_list(api_url, username, password):
    # Fetch file list from the API
    print(f"Fetching file list from API: {api_url}")
    response = requests.get(api_url, auth=(username, password))
    response.raise_for_status()
    files = response.json()  # Get file information as JSON
    print("File list fetched successfully.")
    return files

    ### Example usage
    # api_url = "https://kaartijin-boodja-server/api/publish/cddp-contents/"
    # fetch_file_list(api_url)


@handle_exceptions
def retrieve_file_content(api_url, username, password, file_path):
    # Retrieve file content from the API
    api_url = os.path.join(api_url, 'retrieve-file')
    print(f"Retrieving file content from: {api_url} with filepath: {file_path}")
    response = requests.get(api_url, auth=(username, password), params={'filepath': file_path})
    response.raise_for_status()
    
    # Return the file content
    print("File content retrieved successfully.")
    return response.content


# Start this script
print('Starting the script...')

# Open config file
config_data = read_config_json()

# Fetch file info
files = fetch_file_list(config_data['KB_URL'], config_data['USERNAME'], config_data['PASSWORD'])

if not files:
    print('No files found.')
    sys.exit(0)

# Print total number of files
total_files = len(files)
print(f'Total number of files: {total_files}')

count = 0
for file_info in files:
    count += 1
    print(f"--- File#{count} (out of {total_files}) files ---")

    # Retrieve file contents
    file_content = retrieve_file_content(config_data['KB_URL'], config_data['USERNAME'], config_data['PASSWORD'], file_info['filepath'])
    if file_content:
        # Save file contents locally
        save_file_locally(file_content, file_info['filepath'], config_data['CDDP_ROOT'])
        # Destroy file from the server
        delete_file_remotely(config_data['KB_URL'], config_data['USERNAME'], config_data['PASSWORD'], file_info['filepath'])
