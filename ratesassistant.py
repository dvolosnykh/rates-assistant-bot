from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class CentralBankRussia(Resource):
    def get(self):
        return {'rates': 'no rates yet'}

api.add_resource(CentralBankRussia, '/cbr')

if __name__ == '__main__':
    app.run(debug=True)
