import requests
import os
from django.conf import settings
import boto3
from botocore.exceptions import NoCredentialsError


class S3Operations:
    def __init__(self, url):
        self.url = url

    def download_image(self, file_path):
        os.makedirs(file_path, exist_ok=True)
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                with open(f'{file_path}/image.jpg', 'wb') as f:
                    f.write(response.content)
                print("\n***Image downloaded successfully!\n")
                return self.upload_image(file_path)

            else:
                print(f"\n!!! Failed to download image. Status code: {
                      response.status_code}\n")
        except Exception as e:
            print(f"An error occurred: {e}")

    def upload_image(self, local_path):
        print('\nupload image called....\n')
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        try:
            s3_key = os.path.relpath(
                local_path+"/image.jpg", settings.BASE_DIR)
            print(f'\n\n s3_key:: {s3_key}')

            s3.upload_file(local_path+"/image.jpg", bucket_name, s3_key)

            print("\n***Image uploaded to S3 successfully!\n")

            # Generate URL for the uploaded image
            s3_image_url = f"https://{
                bucket_name}.s3.amazonaws.com/{s3_key}"

            print(f'\n\n\s3_image_url:: {s3_image_url}')

            return s3_image_url
        except NoCredentialsError:
            print("AWS credentials not available.")
            return None
        except Exception as e:
            print(f"An error occurred while uploading to S3: {e}")
            return None
