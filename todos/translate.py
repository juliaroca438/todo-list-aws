import os
import json

from todos import decimalencoder
from todos import todoList
import boto3


def translate(event, context):
    #Obtencion del id pasado en la URL
    Key={
            'id': event['pathParameters']['id']
        }
    
    # Obtencion del componente entero
    # fetch todo from the database
    result = todoList.get_item(Key)
    
    print(result)
    itemJson = json.dumps(result['Item'],cls=decimalencoder.DecimalEncoder)
    # Invocacion de la api de comprehend -> se obtendrá el lenguaje del texto del componente
    comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
    # Parsear la variable del componente a tipo JSON
    jsoncomprehen = json.loads(itemJson)

    # Se aplica la funcion comprehend sobre la entrada del JSON "text". Se obtiene el JSON con los resultados de la API
    langsourceJson=comprehend.detect_dominant_language(Text=jsoncomprehen['text'])
    print(langsourceJson)
    # Variable con el lenguaje del texto obtenido por la api
    langSource=langsourceJson['Languages'][0]['LanguageCode']

    print(langSource)
    # Obtencion del lenguaje pasado por parametro al que se quiere traducir
    targetLanguage={
        'lang': event['pathParameters']['lang']
    }
    # Invocacion de la API translate -> para traducir el texto
    translate = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
    
    # Se traduce el texto. Se le pasa el texto, el lenguaje de entrada y el lenguaje al que traducir
    resultTranslate = translate.translate_text(Text=jsoncomprehen['text'], 
        SourceLanguageCode=langSource, TargetLanguageCode=targetLanguage['lang'])
    
    # Se guarda en la variable JSON del componente el texto traducido
    jsoncomprehen['text'] = resultTranslate['TranslatedText']

    # create a response
    response = {
        "statusCode": 200,
        "body": json.dumps(jsoncomprehen)
    }

    return response
