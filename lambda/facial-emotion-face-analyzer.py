import json
import boto3
from decimal import Decimal
from datetime import datetime
from urllib.parse import unquote_plus

s3 = boto3.client("s3")

rekognition = boto3.client(
    "rekognition",
    region_name="us-east-1"
)

sqs = boto3.client("sqs")

QUEUE_URL = "https://sqs.eu-north-1.amazonaws.com/657082816561/facial-emotion-processing-queue"


def current_time():

    return datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


def analyze_faces(bucket_name, object_key):

    image = s3.get_object(
        Bucket=bucket_name,
        Key=object_key
    )

    image_bytes = image["Body"].read()

    response = rekognition.detect_faces(

        Image={
            "Bytes": image_bytes
        },

        Attributes=[
            "ALL"
        ]

    )

    faces = []

    for index, face in enumerate(
        response["FaceDetails"],
        start=1
    ):

        emotion = face["Emotions"][0]

        gender = "Unknown"

        if "Gender" in face:

            gender = face["Gender"]["Value"]

        faces.append({

            "faceNumber": index,

            "ageRange":
            f"{face['AgeRange']['Low']}-{face['AgeRange']['High']}",

            "gender": gender,

            "smile":
            face["Smile"]["Value"],

            "eyesOpen":
            face["EyesOpen"]["Value"],

            "eyeglasses":
            face["Eyeglasses"]["Value"],

            "sunglasses":
            face["Sunglasses"]["Value"],

            "emotion":
            emotion["Type"],

            "confidence":
            float(
                round(
                    emotion["Confidence"],
                    2
                )
            )

        })

    return faces

def send_to_queue(

    image_name,

    faces

):

    message = {

        "imageName": image_name,

        "faceCount": len(faces),

        "faces": faces,

        "scanTime": current_time()

    }

    sqs.send_message(

        QueueUrl=QUEUE_URL,

        MessageBody=json.dumps(message)

    )


def lambda_handler(event, context):

    try:

        record = event["Records"][0]

        bucket_name = record["s3"]["bucket"]["name"]

        object_key = unquote_plus(

            record["s3"]["object"]["key"]

        )

        print("Bucket :", bucket_name)

        print("Image :", object_key)

        if not object_key.lower().endswith(

            (

                ".jpg",

                ".jpeg",

                ".png",

                ".bmp",

                ".webp"

            )

        ):

            return {

                "statusCode": 200,

                "body": "Skipped"

            }

        faces = analyze_faces(

            bucket_name,

            object_key

        )

        send_to_queue(

            object_key,

            faces

        )

        return {

            "statusCode": 200,

            "body": json.dumps(

                {

                    "message": "Face Analysis Completed",

                    "image": object_key,

                    "facesDetected": len(faces)

                }

            )

        }

    except Exception as e:

        print(str(e))

        return {

            "statusCode": 500,

            "body": json.dumps(

                {

                    "error": str(e)

                }

            )

        }