import requests
import datetime
from forex_python.converter import CurrencyRates

currency_to_convert_to = "GBP"


def collect_prices(from_airport, to_airport, from_date, to_date, price_limit):
    request_string = "https://www.ryanair.com/api/farfnd/3/oneWayFares/{}/{}/cheapestPerDay?outboundDateFrom={}&outboundDateTo={}"\
        .format(from_airport, to_airport, from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d"))
    response = requests.get(request_string)
    data = response.json()
    prices = {}
    currency_rates = CurrencyRates()
    conversion_multiplier = -1
    for current_pos in range(len(data["outbound"]["fares"])):
        if data["outbound"]["fares"][current_pos]["unavailable"]:
            continue
        if conversion_multiplier == -1:
            conversion_multiplier = currency_rates.get_rate(currency_to_convert_to, data["outbound"]["fares"][current_pos]["price"]["currencyCode"])
        if int(data["outbound"]["fares"][current_pos]["price"]["valueMainUnit"]) / conversion_multiplier > price_limit:
            continue

        prices[data["outbound"]["fares"][current_pos]["day"]] = int(
            data["outbound"]["fares"][current_pos]["price"]["value"] / conversion_multiplier)
    return prices


def get_cheapest_trip_date(outbound_prices, inbound_prices, trip_length_days):
    min_price = 100000
    min_out_date = ""
    min_in_date = ""
    for date in outbound_prices:
        date_1 = datetime.datetime.strptime(date, "%Y-%m-%d")
        end_date = date_1 + datetime.timedelta(days=trip_length_days)
        end_date_string = end_date.strftime("%Y-%m-%d")
        if end_date_string in inbound_prices:
            sum_price = outbound_prices[date] + inbound_prices[end_date_string]
            print("Travel {} - {} : {} {}".format(date, end_date_string, sum_price, currency_to_convert_to))
            if sum_price < min_price:
                min_price = sum_price
                min_out_date = date
                min_in_date = end_date_string
    print("Start {} price: {} Back {} price: {}".format(min_out_date,
                                                        outbound_prices[min_out_date],
                                                        min_in_date,
                                                        inbound_prices[min_in_date]))


if __name__ == '__main__':
    outbound_prices = collect_prices("EMA", "DUB", datetime.date.today(), datetime.date.today() + datetime.timedelta(days=6 * 30), 40)
    inbound_prices = collect_prices("DUB", "EMA", datetime.date.today(), datetime.date.today() + datetime.timedelta(days=6 * 30), 40)
    get_cheapest_trip_date(outbound_prices, inbound_prices, 3)
