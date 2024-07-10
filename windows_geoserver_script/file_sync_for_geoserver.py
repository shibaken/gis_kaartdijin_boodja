import sys
import os
import requests
import json

def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An error occurred: {e}")
    return wrapper


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
        

@handle_exceptions
def delete_file_remotely(api_url, username, password, file_path):
    # Destroy the file using the API
    api_url = os.path.join(api_url, 'delete-file')
    response = requests.delete(api_url, auth=(username, password), params={'filepath': file_path})
    response.raise_for_status()
    
    print(f"File [{file_path}] deleted successfully")

    ### Example usage
    # api_url = "https://kaartijin-boodja-server/api/publish/cddp-contents/destroy-file/"
    # file_path = "path/to/file"
    # delete_file(api_url, file_path)


def read_config_json(filename='config.ini'):
    """
    Read JSON data directly from a config.ini file located in the same folder as the script.
    If the file is not found, read from environment variables.
    Args: filename (str): Name of the config file. Default is 'config.ini'.
    Returns: dict: JSON data read from the config file or environment variables.
    """
    config_path = os.path.join(os.path.dirname(__file__), filename)

    if os.path.exists(config_path):
        print(f"Reading JSON data from config file: {config_path}")
        with open(config_path, 'r') as file:
            json_data = json.load(file)
        print("JSON data read successfully.")
    else:
        print(f"Config file '{filename}' not found at path: {config_path}. Falling back to environment variables.")
        json_data = {
            'FILE_SYNC_ENDPOINT_URL': os.getenv('FILE_SYNC_ENDPOINT_URL'),
            'KB_USERNAME': os.getenv('KB_USERNAME'),
            'KB_PASSWORD': os.getenv('KB_PASSWORD'),
            'PATH_TO_GEOSERVER_SECURITY_FOLDER': os.getenv('PATH_TO_GEOSERVER_SECURITY_FOLDER', '/opt/geoserver_data/security/'),
            'MATCHING_SECURITY_FOLDER_NAME': os.getenv('MATCHING_SECURITY_FOLDER_NAME', 'geoserver_security'),
        }
        missing_vars = [key for key, value in json_data.items() if not value]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

    return json_data


def create_folder(folder_path):
    """
    Create a folder at the specified path if it does not exist.
    Args: folder_path (str): Path of the folder to be created.
    """
    # Check if the folder already exists
    if os.path.exists(folder_path):
        print(f"Folder '{folder_path}' already exists.")
    else:
        # Create the folder and its parent directories if they don't exist
        try:
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' created successfully.")
        except OSError as e:
            print(f"Failed to create folder '{folder_path}': {e}")


def save_file_locally(file_content, path_to_geoserver_security_folder, file_path, matching_geoserver_security_folder):
    try:
        # Normalize paths to handle different path separators
        file_path = os.path.normpath(file_path)
        path_to_geoserver_security_folder = os.path.normpath(path_to_geoserver_security_folder)
        matching_geoserver_security_folder = os.path.normpath(matching_geoserver_security_folder)

        # Remove the matching_geoserver_security_folder from file_path if it is present
        if file_path.startswith(matching_geoserver_security_folder):
            file_path = file_path[len(matching_geoserver_security_folder):].lstrip(os.sep)

        # Create the local file path
        local_file_path = os.path.join(path_to_geoserver_security_folder, file_path)

        # Ensure the directory for the local file path exists
        local_file_dir = os.path.dirname(local_file_path)
        if not os.path.exists(local_file_dir):
            os.makedirs(local_file_dir)

        with open(local_file_path, 'wb') as local_file:
            local_file.write(file_content)
        
        file_name = os.path.basename(file_path)
        print(f"File [{file_name}] saved locally successfully")

    except Exception as e:
        print(f"An error occurred while saving the file locally: {e}")


# Start this script
print('Starting the script...')

# Open config file
config_data = read_config_json()

# Create local distination folder
create_folder(config_data['PATH_TO_GEOSERVER_SECURITY_FOLDER'])

# Fetch file info
response = fetch_file_list(config_data['FILE_SYNC_ENDPOINT_URL'], config_data['KB_USERNAME'], config_data['KB_PASSWORD'])
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
    file_content = retrieve_file_content(config_data['FILE_SYNC_ENDPOINT_URL'], config_data['KB_USERNAME'], config_data['KB_PASSWORD'], file_info['filepath'])
    if file_content:
        # Save file contents locally
        save_file_locally(file_content, config_data['PATH_TO_GEOSERVER_SECURITY_FOLDER'], file_info['filepath'], config_data['MATCHING_SECURITY_FOLDER_NAME'])
        # Destroy file from the server
        delete_file_remotely(config_data['FILE_SYNC_ENDPOINT_URL'], config_data['KB_USERNAME'], config_data['KB_PASSWORD'], file_info['filepath'])
