import boto3
from boto3.dynamodb.conditions import Key
import json

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("obituaries-30143076")

def handler(event, context):
    try:
        response = table.query(KeyConditionExpression=Key('stupidID').eq('1'))

        if response['Count'] == 0:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    'data': []
                })
            }
        else:   
            return {
                "statusCode": 200,
                "body": json.dumps({
                    'data': response['Items']
                })
            }

    except Exception as e:
        return {
            "statusCode":404,
            "body":json.dumps({
                    'message':"Error"
            })
        }