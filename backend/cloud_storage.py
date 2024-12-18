import os

from google.cloud import storage
from datetime import datetime, timedelta


class CandidateResumesBucket:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'config/cloud_storage_service_account_key.json'
        self.storage_client = storage.Client()

    
    def upload_resume_to_cloud_storage(self, filename, file):
        bucket = self.storage_client.bucket("candidate_resumes_bucket")

        blob = bucket.blob(filename)
        blob.upload_from_file(file)

        resume_public_url = f"https://storage.googleapis.com/candidate_resumes_bucket/{filename}"

        return resume_public_url


if __name__ == "__main__":
    resume_bucket = CandidateResumesBucket()
    print(resume_bucket.upload_resume_to_cloud_storage("AshwinRajResume.pdf", "temp/AshwinRajResume.pdf"))
