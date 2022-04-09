from concurrent.futures import process
from pymongo import MongoClient
import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv
load_dotenv()


ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")


def s3_upload(processed_file_path, process_code, type):

    session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )
    s3 = session.resource('s3')
    key = f'{type}_{process_code}'
    s3.meta.client.upload_file(
        Bucket='deepcon-processed-minutes', Key=key, Filename=processed_file_path)
    print(f"Upload Successful {type}_{process_code}")


def update_values(process_code: str, processing_status, translated_status):

    processed_transcript_file_path = f"output/processed-transcripts/{process_code}.txt"
    file_path = f'output/meeting-minutes/{process_code}.txt'
    translated_file_path = f"output/meeting-minutes-french/{process_code}.txt"
    status = False
    try:
        conn = MongoClient()
        status = True
        print("Connected successfully!!!")
    except:
        status = False
        print("Could not connect to MongoDB")

    client = MongoClient(
        "mongodb+srv://Majorcms:Majorcms@khoj.nqwbp.mongodb.net/khoj?retryWrites=true&w=majority")
    db = client.MajorCMS
    collection = db.MajorCMS

    s3_upload(processed_transcript_file_path, process_code=process_code, type="transcripts")
    s3_upload(file_path, process_code=process_code, type="minutes")
    s3_upload(translated_file_path, process_code=process_code, type="translated")
    myquery = {"process_code": process_code}
    newvalues = {"$set": {"processing_status": processing_status,
                          'translated_status': translated_status,
                          "processed_transcript_link": f'https://deepcon-processed-minutes.s3.ap-south-1.amazonaws.com/transcripts_{process_code}',
                          "processed_minutes_link": f'https://deepcon-processed-minutes.s3.ap-south-1.amazonaws.com/minutes_{process_code}',
                          "translated_minutes_link": f'https://deepcon-processed-minutes.s3.ap-south-1.amazonaws.com/translated_{process_code}'
                          }}
    res = collection.update_one(myquery, newvalues)

    return status


def find_value(process_code: str):
    client = MongoClient(
        "mongodb+srv://Majorcms:Majorcms@khoj.nqwbp.mongodb.net/khoj?retryWrites=true&w=majority")
    db = client.MajorCMS
    collection = db.MajorCMS

    myquery = {"process_code": process_code}
    mydoc = collection.find(myquery)
    for x in mydoc:
        transcript_link = x["processed_transcript_link"]
        minute_link = x['processed_minutes_link']
        translated_link = x['translated_minutes_link']
    
    return transcript_link, minute_link, translated_link


if __name__ == '__main__':

    x = input('enter process code: ')
    print(find_value(x))
