import json
import requests
import sys
from centralbankrussia import CentralBankRussia

rates_assistant_token = open('ratesassistant.token').read().strip()

result = CentralBankRussia().get_rates(['usd', 'eur'])
if result is None:
    sys.exit()

text = result['date'] + '\n\n'
for rate in result['rates']:
    text += '1 {} = {} RUB\n'.format(rate['currency'], rate['value'])

headers = {
    'Content-Type': 'application/json'
}
data = {
    'chat_id': '@spyrates',
    'text': text
}
response = requests.post('https://api.telegram.org/bot{}/sendMessage'.format(rates_assistant_token), headers=headers, data=json.dumps(data))
print(response.status_code)
if response.status_code != 200:
    print(response.text)
