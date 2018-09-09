from morning_star import MorningStar
from price_fetch import quotes
import pprint
import datetime
import time
import random
import csv
import json


class FinData():

	def __init__(self, ticker):
		self.ticker = ticker
		self.ms = MorningStar()

	def fetch(self):
		pass

	def get_key_metrics(self):

		self.key_ratios = self.ms.get_key_ratios_data(ticker=self.ticker)
		self.income_statement = self.ms.get_income_statement(ticker=self.ticker)
		self.earnings_per_share = float(self.income_statement["earnings_per_share"]["Diluted"])
		self.revenue = float(self.income_statement["general"]["Revenue"])
		self.shares_outstanding = float(self.income_statement["shares_outstanding"]["Diluted"])
		self.free_cash_flow = float(self.ms.get_cash_flow(ticker=self.ticker)["free_cash_flow"]["Free cash flow"])
		self.book_value_per_share = float(self.key_ratios["financials"]["Book Value Per Share * USD"])
		try:
			self.dividend_per_share = float(self.key_ratios["financials"]["Dividends USD"])
		except Exception:
			self.dividend_per_share = 0
		self.EBITDA = float(self.income_statement["shares_outstanding"]["EBITDA"])

		
		# pprint.pprint(self.earnings_per_share)
		# pprint.pprint(self.key_ratios)

		self.quotes = quotes()
		today = datetime.datetime.now()
		today_formatted = today.strftime("%Y-%m-%d")


		# print(today_formatted)
		# self.price = self.quotes.price_fetch(self.ticker, "2018-09-07")[1][0]
		# print("price is %f"%self.price)
		self.price = 200
		return_dict = {}
		return_dict["Price/Earnings"] = self.price/self.earnings_per_share
		return_dict["Price/Sales"] = self.price*self.shares_outstanding/self.revenue
		return_dict["Price/Book"] = self.price/self.book_value_per_share
		return_dict["Dividend Yield"] = self.dividend_per_share/self.price
		return_dict["EBITDA/Free Cash Flow"] = self.EBITDA/self.free_cash_flow


		return return_dict

def read_write_ticks():

	try:
		# ticks = ["LULU","TSLA", "AAPL", "FB", "AMZN", "STM", "GOOGL", "WMT", "AXP", "KO", "MMM", "ABT", "ABBV","ABMD","ACN","ATVI"]
		
		with open("/Users/trevorgordon/Downloads/NASDAQ_full.csv", "r") as f:
			tick_dict = csv.DictReader(f, fieldnames=["Symbol","Description"])

			ticks = [x["Symbol"] for x in tick_dict]

		with open("results.json", "r") as f:
			already_found = json.load(f)


		random.shuffle(ticks)
		failed = []
		max_tries = 5
		for tick_i in ticks:

			if tick_i in already_found.keys():
				continue
			
			trys = 0
			while trys < max_tries:
				try:
					delay = float(random.randint(1, 1000))/10000
					print("Sleeping for %s sec"%delay)
					time.sleep(delay)
					print("Trying %s"%tick_i)
					fd = FinData(tick_i)
					res = fd.get_key_metrics()

					pprint.pprint(res)
					already_found[tick_i] = res
					trys = 0
					break

				except Exception:
					
					trys += 1
					print("Failed for %s\ttry: %i"%(tick_i, trys))
					if trys == max_tries:
						failed.append(tick_i)

		with open("results.json", "w") as f:
			json.dump(already_found, f)
		
		print failed

		print("Failed %i out of %i"%(len(failed), len(ticks)))

	except KeyboardInterrupt:

		with open("results.json", "w") as f:
			json.dump(already_found, f)
		
		print failed

		print("Failed %i out of %i"%(len(failed), len(ticks)))




if __name__ == "__main__":
	

	read_write_ticks()