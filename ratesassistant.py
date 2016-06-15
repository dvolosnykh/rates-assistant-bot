from flask import Flask, abort
from flask_restful import Resource, Api, reqparse
from lxml import etree
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

        request_date = args.get('date')
        if request_date is None:
            response = requests.get('http://www.cbr.ru/scripts/XML_daily_eng.asp')
        else:
            response = requests.get('http://www.cbr.ru/scripts/XML_daily_eng.asp?date_req={}'.format(request_date))
        doc = etree.fromstring(response.content)

        currency_path = "//Valute[CharCode = '{}']/Value/text()".format(currency)
        currencies = doc.xpath(currency_path)
        if len(currencies) > 0:
            date = doc.xpath('/ValCurs/@Date')[0]
            rate = float(currencies[0].replace(',', '.'))
            return {
                'currency': currency,
                'date': date,
                'rate': rate
            }
        else:
            abort(404)


if __name__ == '__main__':
    app.run(debug=True)
