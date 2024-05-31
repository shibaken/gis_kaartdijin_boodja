import requests
import os
import json


def fetch_file_list(api_url, username, password):
    try:
        print('in fetch_file_list')
        print(api_url)
        # Fetch file list from the API
        response = requests.get(api_url, auth=(username, password))
        print(response)
        response.raise_for_status()
        files = response.json()  # Get file information as JSON
        
        print("File List:")
        for file_info in files:
            print(f"- {file_info['filepath']}")
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

    ### Example usage
    # api_url = "https://kaartijin-boodja-server/api/publish/cddp-contents/"
    # fetch_file_list(api_url)


def retrieve_file(api_url, file_path, local_path):
    try:
        # Retrieve file content from the API
        response = requests.get(api_url, params={'filepath': file_path})
        response.raise_for_status()
        
        # Save the file locally
        file_name = os.path.basename(file_path)
        local_file_path = os.path.join(local_path, file_name)
        with open(local_file_path, 'wb') as local_file:
            local_file.write(response.content)
        
        print(f"File [{file_name}] retrieved successfully")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

    ### Example usage
    # api_url = "https://kaartijin-boodja-server/api/publish/cddp-contents/retrieve-file/"
    # file_path = "path/to/file"
    # local_path = "C:/path/on/windows/server"
    # retrieve_file(api_url, file_path, local_path)


def destroy_file(api_url, file_path):
    try:
        # Destroy the file using the API
        response = requests.delete(api_url, params={'filepath': file_path})
        response.raise_for_status()
        
        print(f"File [{file_path}] destroyed successfully")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

    ### Example usage
    # api_url = "https://kaartijin-boodja-server/api/publish/cddp-contents/destroy-file/"
    # file_path = "path/to/file"
    # destroy_file(api_url, file_path)


def read_config_json(filename='config.ini'):
    """
    Read JSON data directly from a config.ini file located in the same folder as the script.

    Args:
        filename (str): Name of the config file. Default is 'config.ini'.

    Returns:
        dict: JSON data read from the config file.
    """
    # Get the absolute path to the config file
    config_path = os.path.join(os.path.dirname(__file__), filename)

    # Check if the config file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file '{filename}' not found.")

    # Read the JSON data from the config file
    with open(config_path, 'r') as file:
        json_data = json.load(file)

    # Return the JSON data
    return json_data



# 1. Open config file
config_data = read_config_json()
print(config_data)

# 2. files = fetch_file_list(pass config here)
api_url = "http://localhost:9071/api/publish/cddp-contents/"
username = "katsufumi"
password = "temp"
fetch_file_list(api_url, username, password)

# 3. for loop in all files:
#     get file
#     copyt to the local in the same path
#     delete file if no errors
#     display message.


