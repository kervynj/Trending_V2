from datetime import date,datetime, timedelta
from database_interface import database_interface
from date_pricing import historical_pricing
import urllib
import csv


class trending_value_screen():

    def __init__(self):

        #api_data_fetch variables
        self.StatPage = 'http://finance.yahoo.com/d/quotes.csv?s='
        self.key = ['Description','Price/Earnings','Price/Sales','Price/Book','DY','MC/EBITDA']

        #six_month variables
        self.BasePage = 'http://finance.yahoo.com/table.csv?s='

        #begin database instance
        self.dtb = database_interface()

    def api_data_fetch(self,ticker):

        findata = {}


        file = self.StatPage + ticker + '&f=' + 'nrp5p6yj1j4'

        #print file

        file_object = urllib.urlopen(file)
        reader = csv.reader(file_object)
        j = 0
        for row in reader:

            findata[self.key[0]] = row[0]
            findata[self.key[1]] = str(self.CurrentDate)

            for i in range(1,5):
                if row[i] == 'N/A':
                    #print ticker
                    findata[self.key[i]] = row[i]
                else:
                    findata[self.key[i]] = round(float(row[i]),3)



            #assign mc/ebitda
            try:
                if row[5] != 'N/A':
                    mc = row[5].split('M')
                    if len(mc) == 2:
                        findata['MC/EBITDA'] = round(float(mc[0])*10**6)
                    else:
                        mc = row[5].split('B')
                        findata['MC/EBITDA'] = round(float(mc[0])*10**9)
                else:
                    print 'No mc/ebitda data for %s' %(ticker)

            except (IndexError,ValueError):
                print 'Error' + file

        #print findata
        return findata

    def sixmonth(self,ticker,date_list):
        #Returns current and previous price for a company based on passed ticker symbol and list of dates
        prices = []

        for d_obj in date_list:

            file = self.BasePage + ticker +'&d='+ str(d_obj.month-1)+'&e='+ str(d_obj.day)+'&f='+str(d_obj.year)+'&g=d&a='+str(d_obj.month-1)+'&b='+ str(d_obj.day) + '&c=' + str(d_obj.year) + '&ignore=.csv'
            file_object = urllib.urlopen(file)
            pricereader = csv.DictReader(file_object)

            for row in pricereader:
                try:
                    prices.append(float(row['Adj Close']))
                except KeyError:
                    print 'No price value for %s on %s' %(ticker,str(d_obj))
                    break

        #calculate price change
        try:
            chng = round(((prices[0]-prices[1])/prices[1])*100,2)
            return chng
        except IndexError:
            print 'Not enough data for' + ticker

    def tsx_ticker_list(self):

        query = "Select Symbol from tsx_companies"
        companies = self.dtb.db_fetch(query)

        return companies

    def upload(self,ticker,data_dict):

        query = "INSERT INTO `results`(`Ticker`, `Date`,`Description`,`Price/Earnings`, `Price/Sales`, `Price/Book`, `Dividend Yield`, `MC/EBITDA`, `Six Month Change`) VALUES ('"+ ticker[0] +"','" + str(self.CurrentDate)+"','"

        for entry in self.key:
            try:
                query += str(data_dict[entry]) + "','"
            except KeyError:
                query += 'N/A' + "','"

        query += data_dict['Six Month Change'] + "','"
        query = query[:-2] + ')'


        #print query
        self.dtb.query_handler(query)

#    def data_ranker(self):





    def main(self):

        #Determine today's date
        self.CurrentDate = date.today()
        #instantiate historical pricing
        self.hp = historical_pricing()

        #Adjust current date to business day
        date_obj = self.hp.DateAdjustment(self.CurrentDate)
        #Fetch previous date obj
        prev_obj = self.hp.MonthDate(date_obj,6)

        l = self.tsx_ticker_list()


        for ticker in l:
            d = self.api_data_fetch(ticker[0])
            price_change = self.sixmonth(ticker[0],[date_obj,prev_obj])
            d['Six Month Change'] = str(price_change)

            self.upload(ticker,d)



x = trending_value_screen()
x.main()