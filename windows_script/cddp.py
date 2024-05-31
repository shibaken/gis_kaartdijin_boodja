import requests
import os


def fetch_file_list(api_url):
    try:
        # Fetch file list from the API
        response = requests.get(api_url)
        response.raise_for_status()
        files = response.json()  # Get file information as JSON
        
        print("File List:")
        for file_info in files:
            print(f"- {file_info['name']}")
    
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

# 1. Open config file
# 2. files = fetch_file_list(pass config here)
# 3. for loop in all files:
#     get file
#     copyt to the local in the same path
#     delete file if no errors
#     display message.


api_url = "https://kaartijin-boodja-server/api/publish/cddp-contents/"
fetch_file_list(api_url)