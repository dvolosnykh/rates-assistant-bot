from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
from centralbankrussia import CentralBankRussia


rates_assistant_token = open('ratesassistant.token').read().strip()

app = Flask(__name__)
api = Api(app)


@api.resource('/bot' + rates_assistant_token)
class RatesAssistant(Resource):
    def post(self):
        data = request.get_json()

        msg = data.get('message')
        if msg is None:
            msg = data.get('edited_message')
        if msg is None:
            abort(400)

        command = msg['text'].split()
        if command[0] == '/cbr':
            currency = command[1] if len(command) > 1 else None

            amount = 1
            try:
                amount = int(command[2]) if len(command) > 2 else 1
            except ValueError:
                try:
                    amount = float(command[2])
                except ValueError:
                    amount = 1

            result = CentralBankRussia().get_rates(currency)
            if result is None:
                abort(503)

            rate = result['rates'][0]
            return {
                'method': 'sendMessage',
                'chat_id': msg['chat']['id'],
                'text': '{} {} = {} RUB    {}'.format(amount, rate['currency'], amount * rate['value'], result['date'])
            }

        abort(400)

@api.resource('/cbr', '/cbr/<currency>')
class Cbr(Resource):
    def get(self, currency=None):
        parser = reqparse.RequestParser()
        parser.add_argument('date')
        args = parser.parse_args()

        result = CentralBankRussia().get_rates(currency, args.get('date'))
        if result is None:
            abort(503)

        rate = result['rates'][0]
        return {
            'currency': rate['currency'],
            'rate': rate['value'],
            'date': result['date']
        }


if __name__ == '__main__':
    app.run(debug=True)
