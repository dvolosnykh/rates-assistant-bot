from flask import Flask, abort
from flask_restful import Resource, Api, reqparse
import requests


app = Flask(__name__)
api = Api(app, '/ratesassistant')


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
        return self.get_yandex_rates(currency, request_date)

    @staticmethod
    def get_yandex_rates(currency, request_date):
        import datetime
        import json

        dict = {
            'usd': 1,
            'eur': 23
        }
        response = requests.get('https://news.yandex.ru/quotes/graph_{}.json'.format(dict.get(currency, 1)))
        if response.status_code != 200:
            return None

        data = response.json()
        prices = data['prices']
        if len(prices) == 0:
            return None

        last_entry = prices[-1]
        date = datetime.date.fromtimestamp(last_entry[0] / 1000).strftime('%d.%m.%Y')
        rate = last_entry[1]
        return {
            'currency': currency,
            'date': date,
            'rate': rate
        }

    @staticmethod
    def get_cbr_rates(currency, request_date):
        from lxml import etree

        if request_date is None:
            response = requests.get('http://www.cbr.ru/scripts/XML_daily_eng.asp')
        else:
            response = requests.get('http://www.cbr.ru/scripts/XML_daily_eng.asp?date_req={}'.format(request_date))

        if response.status_code != 200:
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
