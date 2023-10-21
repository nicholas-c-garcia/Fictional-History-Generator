import requests
import boto3
import json
import os
import hashlib
import time
from requests_toolbelt.multipart import decoder
import base64


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("obituaries-30143076")

client_ssm = boto3.client('ssm')
client_polly = boto3.client('polly', region_name='ca-central-1')

def handler(event, context):

    #____________Info from Frontend___________#
    #Gets info from event
    body = event['body']
    if event["isBase64Encoded"]:
        body = base64.b64decode(body)
    decoded = decoder.MultipartDecoder(body, event['headers']['content-type'])
    parts = decoded.parts
    #print("decoded: ", decoded)
    
    print(parts[0].text)
    print(parts[1].text)
    print(parts[2].text)
    print(parts[3].text)
    print(parts[4].text)
    print(parts[5].text)
    print(parts[6].content)
    
    id = parts[1].text
    name = parts[2].text
    img_name = parts[3].text
    born_year = parts[4].text
    died_year = parts[5].text
    img = parts[6].content
    
    #_____________________________________________#
    
    #Gets ChatGPT API key
    resSSMChatGPT = client_ssm.get_parameters_by_path(
        Path="/api/",
        Recursive=True,
        WithDecryption=True
    )
    
    #API Keys
    apiKey_ChatGPT = resSSMChatGPT['Parameters'][0]['Value']
    apiKey_Cloudinary = resSSMChatGPT['Parameters'][1]['Value']
    apiKey_Cloudinary_S = resSSMChatGPT['Parameters'][2]['Value']

    #_____________________________________________#
    
    #__________________ChatGPT____________________#
    #ChatGPT Stuff
    model = "text-curie-001"
    prompt = f"write an obituary about a fictional character named {name} who was born on {born_year} and died on {died_year}."
    
    headers_chatGPT = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {apiKey_ChatGPT}"
    }

    data_chatGPT = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 100,
        "temperature": 0.5
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/completions", headers=headers_chatGPT, data=json.dumps(data_chatGPT))
        message = response.json()['choices'][0]['text']
    except:
        message = "ChatGPT had an error"
    print("got ChatGPT Response")
    #_____________________________________________#
    
    #Cloudinary info
    cloudinaryName = "dmvumfntz"
    resource_type = "raw"
    urlCloudinary = f"https://api.cloudinary.com/v1_1/{cloudinaryName}/{resource_type}/upload" #Cloudinary api link 
    
    
    #__________________Polly______________________#
    #AWS Polly reads ChatGPT message
    resPolly = client_polly.synthesize_speech(
         Text=message, 
         OutputFormat='mp3', 
         VoiceId='Joanna')

    #Cant post either of these to cloudinary as of 2023-04-20, 1:54AM
    #Saves audio from AWS Polly to /tmp directory with that obituaries ID for its name
    audio_file = os.path.join("/tmp", f'{id}.mp3')
    with open(audio_file, 'wb') as audio_w:
        audio_w.write(resPolly['AudioStream'].read())
        audio_w.close()
        
    body_audio = {
        'api_key'   :  apiKey_Cloudinary
    }
    files_audio = {
        "file" : open(audio_file, 'rb')
    }
    
    #Timestamp and Signature to add to body_audio
    timestamp = int(time.time())
    body_audio['timestamp'] = timestamp
    body_audio['signature'] = create_signature(body_audio, apiKey_Cloudinary_S)
    
    #Post request to cloudinary
    resCloudinary = requests.post(urlCloudinary, files=files_audio, data=body_audio)
    resCloudinary_json = resCloudinary.json()
    print(resCloudinary)
    print(resCloudinary_json)
    
    audio_url = resCloudinary_json['secure_url']
    #_____________________________________________#
    
    #____________________Img______________________#
    resource_type = "image"
    #Puts img into a file
    image_file = os.path.join("/tmp", f'{id}.png')
    with open(image_file, 'wb') as f:
        f.write(img)
        f.close()
        
    body_img = {
        'api_key'   :  apiKey_Cloudinary
    }
    files_img = {
        "file" : open(image_file, 'rb')
    }

    #Timestamp and Signature to add to body_img
    timestamp = int(time.time())
    body_img['timestamp'] = timestamp
    body_img['signature'] = create_signature(body_img, apiKey_Cloudinary_S)
    
    #Post request to cloudinary
    resCloudinary = requests.post(urlCloudinary, files=files_img, data=body_img)
    resCloudinary_json = resCloudinary.json()
    print(resCloudinary)
    print(resCloudinary_json)
    image_url = resCloudinary_json['secure_url']
    
    #_____________________________________________#
    
    print("audio_url: ", audio_url)
    print("image_url: ", image_url)
    print("resPolly: ", resPolly)
    print("working directory: ", os.getcwd())
    print("working directory contents:", os.listdir("/var/task"))
    print("tmp directory contents:", os.listdir("/tmp"))
    
    response_ChatGPT = {
        "output"    :   message,
        "audio"     :   audio_url,     
        "img"       :   image_url,
        "name"      :   name,
        "year_born" :   born_year,
        "year_died" :   died_year,
        "id"        :   id,
        "stupidID"  :   '1'
    }

    
    #return response_ChatGPT
    try:
        table.put_item(Item=response_ChatGPT)
        return{
            "statusCode":200,
            "body": json.dumps({"data":response_ChatGPT})
        }
    
    except Exception as exception:
        return{
            "statusCode":500,
            "body":json.dumps({"message":str(exception)})       
        }
        
def create_signature(body, api_secret):
    exclude = ["api_key", "resource_type", "cloud_name"]
    sorted_body = sort_dictionary(body, exclude)
    query_string = create_query_string(sorted_body)
    query_string_ap = f'{query_string}{api_secret}'
    hashed = hashlib.sha1(query_string_ap.encode())
    signature = hashed.hexdigest()
    return signature
    
def sort_dictionary(dictionary, exclude):
    return {k: v for k, v in sorted(dictionary.items(), key=lambda item: item[0]) if k not in exclude}

def create_query_string(body):
    query_string = ""
    for i, (k, v) in enumerate(body.items()):
        query_string = f'{k}={v}' if i == 0 else f'{query_string}&{k}={v}'
    
    return query_string
