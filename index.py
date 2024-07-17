import json
import boto3
import requests
from message import *
from config import BOT_TOKEN
from boto3.dynamodb.conditions import Attr


def handler(event, context):
    #получение текста и chatid из отправленного сообщения боту
    body = json.loads(event['body'])
    message = body['message']
    chatId = message['chat']['id']
    #словарь зарезервированных слов
    keyText = {"/start": start, "Справка": helpmessage, "NotFound": incorr}
    #подключение к БД YDB
    database = boto3.resource(
                            'dynamodb',
    #ссылка подключения к базе указывается в кавычках
                            endpoint_url="",
                            )
    #выбор таблицы     
    table = database.Table('table430')

    #поиск и вывод результатов
    def send_result(tableSearch: str,textSearch: str):
        ''' 
        Поиск в cтолбце 'number' или 'name' текста из переменной text, полученной
        от телеграмм бота.
         '''
        response = table.scan(
            FilterExpression=Attr(tableSearch).eq(textSearch)
        )
        filtered_items = response['Items']
        if response['Count'] == 1:
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                filtered_items.extend(response['Items'])
            sendText = 'ПС ' + filtered_items[0]['number'] + '_' + filtered_items[0]['name'] + '\n' + filtered_items[0]['address']
            url = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage'
            data = {
                'chat_id': chatId,
                'text': sendText
                }
            requests.request("POST", url, data=data)
            print('Ok')
        else:
            url = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage'
            data = {
                'chat_id': chatId,
                'text': keyText['NotFound']
                }
            requests.request("POST", url, data=data)
    #проверка на текстовое сообщение
    if not 'text' in message:
        text = 'Неправильный формат сообщения, отправьте текстовое сообщение.'
        url = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage'
        data = {
            'chat_id': chatId,
            'text': text 
        }
        r = requests.request("POST", url, data = data)
    else:
        text = message['text'].capitalize()
        if text.isdigit():
            send_result('number', text)
        else:
            if text in keyText:
                url = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage'
                data = {
                        'chat_id': chatId,
                        'text': keyText[text]
                        }
                requests.request("POST", url, data=data)
            else:    
                send_result('name', text)