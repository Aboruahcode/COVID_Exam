import pandas as pd
import json
import requests
from datetime import datetime
from typing import Dict, List

def create_observation(record: pd.Series) -> Dict:
    """
    Creates an Observation resource for a single record of COVID-19 case data.
    """
    return {
        "resourceType": "Observation",
        "id": f"observation-{record['dateRep']}",
        "status": "final",
        "code": {
            "coding": [
                {"system": "http://loinc.org", "code": "94531-1", "display": "COVID-19 cases reported"}
            ]
        },
        "subject": {
            "reference": f"Country/{record['countryterritoryCode']}"
        },
        "effectiveDateTime": record['dateRep'],
        "valueQuantity": {
            "value": record['cases'],
            "unit": "count",
            "system": "http://unitsofmeasure.org",
            "code": "count"
        }
    }

def create_fhir_bundle(data_path: str, output_path: str):
    """
    Creates a FHIR bundle from a JSON file containing filtered European COVID-19 data.
    """
    data = pd.read_json(data_path)
    fhir_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "fullUrl": f"urn:uuid:observation-{row['dateRep']}",
                "resource": create_observation(row)
            } for index, row in data.iterrows()
        ]
    }

    with open(output_path, 'w') as f:
        json.dump(fhir_bundle, f, indent=4)

    print("FHIR bundle created successfully.")
    return fhir_bundle

def reverse_fhir_bundle(bundle_path: str) -> List[Dict]:
    """
    Reverses a FHIR bundle back to a list of dictionaries representing the original data.
    """
    with open(bundle_path, 'r') as f:
        fhir_bundle = json.load(f)

    reversed_data = []
    for entry in fhir_bundle.get('entry', []):
        observation = entry.get('resource', {})
        date_rep = observation.get('effectiveDateTime', '')
        try:
            parsed_date = datetime.strptime(date_rep, "%Y-%m-%d")
        except ValueError:
            parsed_date = datetime.strptime(date_rep, "%d/%m/%Y")
        date_rep = parsed_date.strftime("%d/%m/%Y")
        cases = observation.get('valueQuantity', {}).get('value', 0)
        reversed_entry = {
            'dateRep': date_rep,
            'cases': cases,
            'countryterritoryCode': observation.get('subject', {}).get('reference', '').split('/')[-1]
        }
        reversed_data.append(reversed_entry)

    return reversed_data

def send_fhir_bundle(fhir_bundle, server_url):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(server_url, json=fhir_bundle, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send data: {e}")
        return None

if __name__ == "__main__":
    # File paths and server URL
    data_path = '../COVID_Exam/Backend/style/filtered_european_data.json'
    output_path = '../fhir_bundle.json'
    server_url = 'http://127.0.0.1:8000/receive_fhir/'

    # Create and send FHIR Bundle
    fhir_bundle = create_fhir_bundle(data_path, output_path)
    response = send_fhir_bundle(fhir_bundle, server_url)
    print("Server response:", response)

    # Optional: Reverse FHIR Bundle
    reversed_data = reverse_fhir_bundle(output_path)
    print("Reversed data:", reversed_data)