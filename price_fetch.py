import quandl

class quotes(object):
	
	def __init__(self):
		quandl.ApiConfig.api_key = 'aqaqfvVVypE4taXrqpZQ'
		
	def price_fetch(self, symbol, date, end_date=''):
	
		prices = []
		succ = True

		if end_date == '':
			response = quandl.get_table('SHARADAR/SEP', date='{0}'.format(str(date)), ticker=symbol)
		else:
			response = 	quandl.get_table('SHARADAR/SEP', date='{0},{1}'.format(str(date), str(end_date)), ticker=symbol)

		data = response.to_dict()

		for key,entry in enumerate(data['close']):
			prices.append(data['close'][key])

		return succ, prices
		
if __name__ == "__main__":

	x = quotes()
	l, p = x.price_fetch("AAPL", "2017-01-05", "2017-10-30")
	