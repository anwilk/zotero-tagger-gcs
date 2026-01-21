import configparser
import json
from pyzotero import zotero

def fetch_zotero_items():
    """
    Fetches items from a Zotero library and saves them to a JSON file.

    This function reads Zotero API credentials from a 'config.ini' file,
    connects to the Zotero library, and retrieves all items. It then
    filters for items that have an abstract, extracts relevant information,
    and saves the data to 'data/zotero_items.json'.
    """
    config = configparser.ConfigParser()
    config.read('config.ini')

    library_id = config['zotero']['library_id']
    api_key = config['zotero']['api_key']
    library_type = config['zotero']['library_type']

    # Check if the credentials are still the default values
    if library_id == 'YOUR_LIBRARY_ID' or api_key == 'YOUR_API_KEY':
        print("Please update the 'config.ini' file with your Zotero library ID and API key.")
        print("You can find this information at https://www.zotero.org/settings/keys")
        return

    zot = zotero.Zotero(library_id, library_type, api_key)
    
    print("Fetching items from Zotero... this may take a while.")
    items = zot.top(limit=None)
    
    extracted_data = []
    for item in items:
        # We are only interested in items with abstracts.
        if 'abstractNote' in item['data'] and item['data']['abstractNote']:
            data = {
                'key': item['key'],
                'title': item['data'].get('title', ''),
                'abstract': item['data'].get('abstractNote', ''),
                'tags': item['data'].get('tags', [])
            }
            extracted_data.append(data)

    output_file = 'data/zotero_items.json'
    with open(output_file, 'w') as f:
        json.dump(extracted_data, f, indent=4)

    print(f"Successfully fetched {len(extracted_data)} items with abstracts and saved them to {output_file}")

if __name__ == '__main__':
    fetch_zotero_items()
