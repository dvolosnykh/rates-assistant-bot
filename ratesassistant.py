from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import requests

rates_assistant_token = open('ratesassistant.token').read().strip()

app = Flask(__name__)
api = Api(app)


@api.resource('/bot' + rates_assistant_token)
class RatesAssistant(Resource):
    def post(self):
        data = request.get_json()
        print(data)

        msg = data.get('message')
        if msg is None:
            msg = data.get('edited_message')
        if msg is None:
            return None

        command = msg['text'].split()
        if command[0] == '/cbr':
            cbr = CentralBankRussia()
            currency = command[1] if len(command) > 1 else 'usd'
            result = cbr.get(currency)

            amount = 1
            try:
                amount = int(command[2]) if len(command) > 2 else 1
            except ValueError:
                try:
                    amount = float(command[2])
                except ValueError:
                    amount = 1

            return {
                'method': 'sendMessage',
                'chat_id': msg['chat']['id'],
                'text': '{} {} = {} RUB    {}'.format(amount, result['currency'], amount * result['rate'], result['date'])
            }

        return None

@api.resource('/cbr', '/cbr/<currency>')
class CentralBankRussia(Resource):
    def get(self, currency=None):
        if currency is None:
            currency = 'usd'
        currency = currency.upper()

        parser = reqparse.RequestParser()
        parser.add_argument('date')
        args = parser.parse_args()

        data = self.get_rates(currency, args.get('date'))
        if data is not None:
            return data
        else:
            abort(404)

    def get_rates(self, currency, request_date):
        from lxml import etree

        if request_date is None:
            response = requests.get('http://www.cbr.ru/scripts/XML_daily_eng.asp')
        else:
            response = requests.get('http://www.cbr.ru/scripts/XML_daily_eng.asp?date_req={}'.format(request_date))

        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            return None

        doc = etree.fromstring(response.content)
        currency_path = "//Valute[CharCode = '{}']/Value/text()".format(currency)
        currencies = doc.xpath(currency_path)
        if len(currencies) == 0:
            return None

        date = doc.xpath('/ValCurs/@Date')[0]
        rate = float(currencies[0].replace(',', '.'))
        return {
            'currency': currency,
            'date': date,
            'rate': rate
        }


if __name__ == '__main__':
    app.run(debug=True)
