#!/usr/bin/python3

from bs4 import BeautifulSoup
from requests import Session as rq_Session
from requests import exceptions as rq_exceptions
from datetime import datetime
from pytz import timezone
from json import dumps as json_dumps
from json import loads as json_loads

# Definitionen URL
hostname = 'tibber.com'
scheme = 'https'
postalCode = '86633'
tz = 'Europe/Berlin'

# Headers
headers = {
    'User-Agent': 'Mozilla/5.0'
}

error = ''
status = ''

try:
    session = rq_Session()
    # download Sites
    url = f'{scheme}://{hostname}/de/api/lookup/price-overview'
    params = {
        "postalCode": postalCode
    }
    response = session.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    if (response.headers._store['content-type'][1] == 'application/json; charset=utf-8'):
        current_datetime = datetime.now(timezone(tz))
        
        response_json = json_loads(response.text)
        # TODO: aktuelle Stunde auslesen
        priceIncludingVat = response_json['energy']['todayHours'][current_datetime.hour]['priceIncludingVat']
        priceExcludingVat = response_json['energy']['todayHours'][current_datetime.hour]['priceExcludingVat']

    status = 'OK'
except rq_exceptions.ConnectTimeout:
    error = f'Fehler {hostname} nicht erreichbar'
except rq_exceptions.ConnectionError:
    error = f'Fehler {hostname} nicht erreichbar'
except Exception as e:
    error = f'Fehler {hostname} verändert'

if error != '':
    json_payload = {
        'Status' : 'unknown',
        'Error' : error
    }
elif status != '':
    json_payload = {
        'Status' : status,
        'Data' : {
            'priceIncludingVat' : priceIncludingVat,
            'priceExcludingVat' : priceExcludingVat
            },
        'Error' : 'kein Fehler'
    }
else:
    json_payload = {
        'Status' : 'unknown',
        'Error' : 'unknown'
    }

print(json_dumps(json_payload, indent=4))

