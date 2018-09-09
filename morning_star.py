import pandas as pd
import requests
import csv
import pprint
import time


class MorningStar():


	def __init__(self):
		pass


	def connect(self):

		pass

	def build_key_ratios_request(self, ticker):
		return "http://financials.morningstar.com/ajax/exportKR2CSV.html?t=%s"%ticker

	def build_request(self, *args, **kwargs):
		url = ""
		baseurl = "http://financials.morningstar.com/ajax/ReportProcess4CSV.html?"
		
		ticker = kwargs.get('ticker',"TWTR")
		report_type = kwargs.get('report_type',"is")
		period = kwargs.get('period',12)
		data_type = kwargs.get('data_type',"A")
		order = kwargs.get('order',"asc")
		column_year = kwargs.get('column_year',5)
		number = kwargs.get('number',3)

		url += baseurl
		url+="t=%s"%ticker
		url+="&reportType=%s"%report_type
		url+="&period=%i"%period
		url+="&dataType=%s"%data_type
		url+="&order=%s"%order
		url+="&columnYear=%i"%column_year
		url+="&number=%i"%number

		return url

	def get_data(self, url):


		resp = requests.get(url)
		lines = []
		for line in csv.reader(resp.iter_lines()):
			lines.append(line)
		if len(lines) == 0:
			raise IOError("Did not get a response from website")

		df = pd.DataFrame(lines)
		
		return df

	def clean_and_swap(self, df):

		# df.iloc[0,0] = "time"
		df = df.T
		df.columns = df.iloc[0]
		df = df.iloc[1:]
		# df = df.reindex(df.index.drop(0))
		# df.set_index(df.iloc[0], inplace=True)
		df.set_index(list(df.columns[[0]]))
		return df

	def get_income_statement(self, *args, **kwargs):

		url = self.build_request(*args, **kwargs)
		df = self.get_data(url)

		return_dict = {}
		return_dict["general"] = self.helper(df, 0, 4)
		return_dict["operating_expenses"] = self.helper(df, 5, 16)
		return_dict["earnings_per_share"] = self.helper(df, 18, 20)
		return_dict["shares_outstanding"] = self.helper(df, 21, 24)
		return return_dict

	def helper(self, df, start, stop):

		df2 = df.iloc[start:stop,:]
		df2= self.clean_and_swap(df2)
		df2 = df2.tail(1).iloc[0]
		return df2.to_dict()
		return df2


	def get_key_ratios_data(self, *args, **kwargs):

		url = self.build_key_ratios_request(*args, **kwargs)
		df = self.get_data(url)

		return_dict = {}

		return_dict["financials"] = self.helper(df, 1, 17)
		return_dict["key_ratios"] = self.helper(df, 19, 29)
		return_dict["profitability"] = self.helper(df, 30, 39)
		return_dict["growth"] = self.helper(df, 41, 62)
		return_dict["cash_flow"] = self.helper(df, 64, 69)
		return_dict["balance_sheet_items"] = self.helper(df, 72, 93)
		return_dict["liquidity"] = self.helper(df, 94, 100)
		return_dict["efficiency"] = self.helper(df, 101, 110)

		return return_dict

	def get_cash_flow(self, *args, **kwargs):
		url = self.build_request(report_type="cf", *args, **kwargs)
		df = self.get_data(url)

		return_dict = {}
		return_dict["free_cash_flow"] = self.helper(df, 35, 38)
		return return_dict


	def get_recent(self, ticker, col):
		five_years = self.get_data(
						ticker=ticker,
						order="desc")
		last_year = five_years.loc["2017-09",col]
		return last_year


if __name__ == "__main__":

	ms = MorningStar()
	# data = ms.get_income_statement("TWTR")
	# data = ms.get_key_ratios_data("AAPL")
	# data = ms.get_recent("AAPL", "Revenue")
	data = ms.get_cash_flow("TWTR")

	

	pprint.pprint(data)




