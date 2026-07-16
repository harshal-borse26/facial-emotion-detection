import json
import uuid
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("FaceEmotionResults")


def convert_faces(faces):

    converted = []

    for face in faces:

        converted.append({

            "faceNumber": face["faceNumber"],

            "ageRange": face["ageRange"],

            "gender": face["gender"],

            "smile": face["smile"],

            "eyesOpen": face["eyesOpen"],

            "eyeglasses": face["eyeglasses"],

            "sunglasses": face["sunglasses"],

            "emotion": face["emotion"],

            "confidence": Decimal(
                str(face["confidence"])
            )

        })

    return converted


def save_result(message):

    table.put_item(

        Item={

            "imageId":
            "IMG_" + str(uuid.uuid4())[:8],

            "imageName":
            message["imageName"],

            "faceCount":
            message["faceCount"],

            "faces":
            convert_faces(
                message["faces"]
            ),

            "scanTime":
            message["scanTime"]

        }

    )

def lambda_handler(event, context):

    try:

        for record in event["Records"]:

            message = json.loads(

                record["body"]

            )

            save_result(

                message

            )

        return {

            "statusCode": 200,

            "body": json.dumps(

                {

                    "message": "Face Emotion Data Stored Successfully"

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