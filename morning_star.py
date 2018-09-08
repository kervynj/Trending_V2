import pandas as pd
import requests
import csv
import pprint



class MorningStar():


	def __init__(self):
		pass


	def connect(self):

		pass

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


	def get_data(self, *args, **kwargs):

		url = self.build_request(*args, **kwargs)

		resp = requests.get(url)
		lines = []
		for line in csv.reader(resp.iter_lines()):
			lines.append(line)

		lines = lines[1:-1]
		df = pd.DataFrame(lines)
		df.loc[0,0] = "time"
		df = df.T
		df.columns = df.iloc[0]
		df = df.reindex(df.index.drop(0))
		df.set_index('time', inplace=True)
		# df.drop(df.index[1], inplace=True)
		return df

	def get_all_recent(self, ticker):
		five_years = self.get_data(
						ticker=ticker,
						order="desc")
		last_year = five_years.loc["2017-09",:].to_dict()
		return last_year

	def get_recent(self, ticker, col):
		five_years = self.get_data(
						ticker=ticker,
						order="desc")
		last_year = five_years.loc["2017-09",col]
		return last_year


if __name__ == "__main__":

	ms = MorningStar()
	data = ms.get_all_recent("AAPL")
	# data = ms.get_recent("AAPL", "Revenue")
	pprint.pprint(data)




