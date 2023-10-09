import os
from azure.storage.blob import BlobServiceClient
import requests
import uuid


class AzureBlobStorageManager:
    def __init__(self, STORAGEACCOUNTURL, STORAGEACCOUNTKEY, CONTAINERNAME):
        self.STORAGEACCOUNTURL = STORAGEACCOUNTURL
        self.STORAGEACCOUNTKEY = STORAGEACCOUNTKEY
        self.CONTAINERNAME = CONTAINERNAME
        self.blob_service_client_instance = BlobServiceClient(account_url=self.STORAGEACCOUNTURL, credential=self.STORAGEACCOUNTKEY)

    def upload_file(self, file):
        if file:
            file_name = file.name
            blob_client_instance = self.blob_service_client_instance.get_blob_client(container=self.CONTAINERNAME, blob=file_name)

            with file as data:
                blob_client_instance.upload_blob(data, overwrite=True)

            return file_name

    def read_blob_data(self, file_name):
        blob_client_instance = self.blob_service_client_instance.get_blob_client(container=self.CONTAINERNAME, blob=file_name)
        blob_data = blob_client_instance.download_blob()
        data = blob_data.readall().decode('utf-8')
        return data

    def list_blob_files(self):
        try:
            container_client = self.blob_service_client_instance.get_container_client(self.CONTAINERNAME)
            blob_files = []

            for blob in container_client.list_blobs():
                blob_files.append(blob.name)

            return blob_files
        except Exception as e:
            print(f"Error listing blob files: {str(e)}")
            return []
        
def tanslator(key, endpoint, location, path, text_content, target_language):
    try:
        constructed_url = endpoint + path

        params = {
            'api-version': '3.0',
            'from': 'en',
            'to': [target_language]  # Use the selected target language
        }

        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Ocp-Apim-Subscription-Region': location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        body = [{
            'text': text_content
        }]

        request = requests.post(constructed_url, params=params, headers=headers, json=body)
        response = request.json()

        # Extract the translated text from the response
        return response[0]['translations'][0]['text']

    except Exception as e:
        return str(e)
    
def calculate_cost(response, cost_per_token=0.00002):
    """
    Calculate the cost of the OpenAI API response based on the number of tokens.

    Parameters:
        response: The OpenAI API response object.
        cost_per_token (float): Based on the OpenAI website, the text-davinci-003 model is $0.02 per 1000 tokens

    Returns:
        float: The calculated cost and other details adding up to cost
    """
    try: 
        usage = response.usage
        pt=usage.prompt_tokens #can be removed
        ct=usage.completion_tokens #can be removed
        input_cost=pt * cost_per_token #can be removed
        generative_cost=ct * cost_per_token #can be removed
        total_tokens = usage.total_tokens 
        cost = total_tokens * cost_per_token

        return cost,total_tokens,input_cost,pt,generative_cost,ct
    except AttributeError:
        return 0.0