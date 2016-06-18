from lxml import etree
import requests
import sys

class CentralBankRussia:
    def get_rates(self, currency=None, request_date=None):
        if request_date is None:
            response = requests.get('http://www.cbr.ru/scripts/XML_daily_eng.asp')
        else:
            response = requests.get('http://www.cbr.ru/scripts/XML_daily_eng.asp?date_req={}'.format(request_date))

        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            return None

        doc = etree.fromstring(response.content)
        date = doc.xpath('/ValCurs/@Date')[0]

        if currency is None:
            currency = 'usd'
        if type(currency) is not list:
            currency = [currency]

        rates = []
        for c in currency:
            c = c.upper()
            currency_path = "//Valute[CharCode = '{}']/Value/text()".format(c)
            values = doc.xpath(currency_path)
            if len(values) == 0:
                pass

            value = float(values[0].replace(',', '.'))
            rates.append({
                'currency': c,
                'value': value
            })

        return {
            'rates': rates,
            'date': date
        }


if __name__ == '__main__':
    currency = sys.argv[1] if len(sys.argv) > 1 else None
    date = sys.argv[2] if len(sys.argv) > 2 else None
    result = CentralBankRussia().get_rates(currency, date)
    print(result)
