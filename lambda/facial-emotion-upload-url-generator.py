import json
import boto3
from decimal import Decimal
from botocore.config import Config

s3 = boto3.client(
    "s3",
    region_name="eu-north-1",
    endpoint_url="https://s3.eu-north-1.amazonaws.com",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "virtual"}
    )
)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("FaceEmotionResults")
BUCKET_NAME = "facial-emotion-image-upload-2026"

def response(status, body):

    return {

        "statusCode": status,

        "headers": {

            "Access-Control-Allow-Origin": "*",

            "Access-Control-Allow-Headers": "Content-Type",

            "Access-Control-Allow-Methods": "GET,OPTIONS"

        },

        "body": json.dumps(body)

    }

def decimal_converter(obj):

    if isinstance(obj, Decimal):

        return float(obj)

    raise TypeError


def get_results():

    result = table.scan()

    items = result.get("Items", [])

    items.sort(

        key=lambda x: x["scanTime"],

        reverse=True

    )

    return {

        "statusCode": 200,

        "headers": {

            "Access-Control-Allow-Origin": "*",

            "Access-Control-Allow-Headers": "Content-Type",

            "Access-Control-Allow-Methods": "GET,OPTIONS"

        },

        "body": json.dumps(

            items,

            default=decimal_converter

        )

    }

def lambda_handler(event, context):

    if event["httpMethod"] == "OPTIONS":

        return response(
            200,
            {
                "message": "OK"
            }
        )

    path = event.get("resource", "")

    if path == "/results":

        return get_results()

    elif path == "/upload":

        params = event.get("queryStringParameters") or {}

        file_name = params.get("fileName")

        if not file_name:

            return response(
                400,
                {
                    "message": "fileName is required"
                }
            )

        upload_url = s3.generate_presigned_url(

            "put_object",

            Params={

                "Bucket": BUCKET_NAME,

                "Key": file_name

            },

            ExpiresIn=300

        )

        return response(

            200,

            {

                "uploadUrl": upload_url,

                "fileName": file_name

            }

        )

    else:

        return response(

            404,

            {

                "message": "Invalid API Endpoint"

            }

        )