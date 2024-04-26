import requests
import os

def download_json(url, filename):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'w') as file:
            file.write(response.text)
        print("File downloaded successfully.")
    else:
        print("Failed to retrieve the file. Status Code:", response.status_code)

if __name__ == "__main__":
    # Specify the path to the Backend directory
    download_json('https://opendata.ecdc.europa.eu/covid19/casedistribution/json/', 'Backend/Covid_19.json')
