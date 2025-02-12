import os

from config.settings import Settings
from fastapi import status
from fastapi.exceptions import HTTPException
from google.cloud import storage
from google.cloud.exceptions import NotFound

project_id = Settings.PROJECT_ID
bucket_name = Settings.BUCKET_NAME
image_path = Settings.IMAGE_PATH
document_path = Settings.DOCUMENT_PATH
audio_path = Settings.AUDIO_PATH
video_path = Settings.VIDEO_PATH

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'service_account.json'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath('service_account.json')

class GCStorage:
    # @staticmethod 
    def __init__(self):
        self.client_storage = storage.Client()
        self.bucket_name = bucket_name

    def upload_file_to_gcp(self, url, type, filename):
        if url is not None:
            if type == "Image":
                bucket = self.client_storage.get_bucket(self.bucket_name)
                imagePath = image_path + "/" + filename
                blob = bucket.blob(imagePath)
                blob.upload_from_file(url.file)
                flyer_url = f'https://storage.googleapis.com/{self.bucket_name}/{imagePath}'
                return flyer_url

            elif type == "Document":
                bucket = self.client_storage.get_bucket(self.bucket_name)
                documentPath = document_path + "/" + filename
                blob = bucket.blob(documentPath)
                blob.upload_from_file(url.file)
                outline_url = f'https://storage.googleapis.com/{self.bucket_name}/{documentPath}'
                return outline_url

            elif type == "Audio":
                bucket = self.client_storage.get_bucket(self.bucket_name)
                audioPath = audio_path + "/" + filename
                blob = bucket.blob(audioPath)
                blob.upload_from_file(url.file)
                logo_url = f'https://storage.googleapis.com/{self.bucket_name}/{audioPath}'
                return logo_url

            elif type == "Video":
                bucket = self.client_storage.get_bucket(self.bucket_name)
                videoPath = video_path + "/" + filename
                blob = bucket.blob(videoPath)
                blob.upload_from_file(url.file)
                logo_url = f'https://storage.googleapis.com/{self.bucket_name}/{videoPath}'
                return logo_url
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File type should be eg. Image, Document, Audio, Video"
                )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload a valid file"
        )

    def delete_file_to_gcp(self, type, filename):
        if filename is not None:
            if type == "Image":
                try:
                    bucket = self.client_storage.get_bucket(self.bucket_name)
                    imagePath = image_path + "/" + filename
                    blob = bucket.blob(imagePath)
                    blob.delete()
                except NotFound:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'🚨Flyer does not exist - do something'
                    )
            elif type == "Document":
                try:
                    bucket = self.client_storage.get_bucket(self.bucket_name)
                    flyer_path = document_path + "/" + filename
                    blob = bucket.blob(flyer_path)
                    blob.delete()
                except NotFound:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'🚨 Document does not exist - do something'
                    )
            elif type == "Audio":
                try:
                    bucket = self.client_storage.get_bucket(self.bucket_name)
                    audioPath = audio_path + "/" + filename
                    blob = bucket.blob(audioPath)
                    blob.delete()
                except NotFound:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'🚨 Logo does not exist - do something'
                    )
            elif type == "Video":
                try:
                    bucket = self.client_storage.get_bucket(self.bucket_name)
                    videoPath = video_path + "/" + filename
                    blob = bucket.blob(videoPath)
                    blob.delete()
                except NotFound:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'🚨 Logo does not exist - do something'
                    )
        return "File delete successful from GCP"
