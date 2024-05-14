import requests
import os
from django.conf import settings
import boto3
from botocore.exceptions import NoCredentialsError
import shutil
import random


class S3Operations:
    def __init__(self, url):
        self.url = url

    def download_image(self, file_path):
        os.makedirs(file_path, exist_ok=True)
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                # Generate a random 4-digit number
                random_number = random.randint(100, 999999)
                                
                # Construct the filename with the random number
                filename = f"image_{random_number}.jpg"
                
                # Construct the full file path
                file_path = os.path.join(file_path, filename)
                print(f'\n\n ------file_path:: {file_path}------ \n\n')
                
                # Save the image with the new filename
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print("\n***Image downloaded successfully!\n")
                
                return self.upload_image(file_path)
            else:
                print(f"\n!!! Failed to download image. Status code: {response.status_code}\n")
        except Exception as e:
            print(f"An error occurred: {e}")
            
    def upload_image(self, local_path):
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        try:
            # Extract the filename from the file path
            filename = os.path.basename(local_path)
            print(f'\n\n\n ------------------ filename:: {filename} --------\n\n')

            # Define the S3 key by removing the 'static/tempImages/' prefix
            s3_key_name = os.path.relpath(local_path, settings.BASE_DIR)
            s3_key = s3_key_name.replace('static/tempImages/', '')

            print(f'\n\n s3_key:: {s3_key}')
            s3.upload_file(local_path, bucket_name, s3_key)

            print("\n***Image uploaded to S3 successfully!\n")

            # Generate URL for the uploaded image
            s3_image_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"

            print(f'\n\n s3_image_url:: {s3_image_url}')
            
            # delete from local
            self.delete_local_folder(local_path)
            
            return s3_image_url
        except NoCredentialsError:
            print("AWS credentials not available.")
            return None
        except Exception as e:
            print(f"An error occurred while uploading to S3: {e}")
            return None
        
    def delete_local_folder(self, local_folder_path):
        try:
            parent_folder_path = os.path.dirname(local_folder_path)
            shutil.rmtree(parent_folder_path)
            print(f"\nFolder '{parent_folder_path}' deleted successfully.")
        except Exception as e:
            print(f"Failed to delete folder '{local_folder_path}': {e}")
