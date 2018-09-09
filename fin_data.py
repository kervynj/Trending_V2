from morning_star import MorningStar
# from mitches_dumb_script import get_price_data
import pprint



class FinData():

	def __init__(self, ticker):
		self.ticker = ticker
		self.ms = MorningStar()

	def fetch(self):
		pass

	def get_key_metrics(self):

		self.key_ratios = self.ms.get_key_ratios_data(self.ticker)
		self.income_statement = self.ms.get_income_statement(self.ticker)
		self.earnings_per_share = float(self.income_statement["earnings_per_share"]["Diluted"])
		self.revenue = float(self.income_statement["general"]["Revenue"])
		self.shares_outstanding = float(self.income_statement["shares_outstanding"]["Diluted"])
		self.free_cash_flow = float(self.ms.get_cash_flow(ticker=self.ticker)["free_cash_flow"]["Free cash flow"])
		self.book_value_per_share = float(self.key_ratios["financials"]["Book Value Per Share * USD"])
		self.dividend_per_share = float(self.key_ratios["financials"]["Dividends USD"])
		self.EBITDA = float(self.income_statement["shares_outstanding"]["EBITDA"])

		# self.price = get_price_data(self.ticker)
		self.price = 100
		return_dict = {}
		return_dict["Price/Earnings"] = self.price/self.earnings_per_share
		return_dict["Price/Sales"] = self.price*self.shares_outstanding/self.revenue
		return_dict["Price/Book"] = self.price/self.book_value_per_share
		return_dict["Dividend Yield"] = self.dividend_per_share/self.price
		return_dict["EBITDA/Free Cash Flow"] = self.EBITDA/self.free_cash_flow


		return return_dict



if __name__ == "__main__":

	fd = FinData("AAPL")
	res = fd.get_key_metrics()

	pprint.pprint(res)