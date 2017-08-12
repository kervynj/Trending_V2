from datetime import date,datetime, timedelta
from database_interface import database_interface
from date_pricing import historical_pricing
import urllib
import csv
import get_quotes


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
        status = True
        try:
            file_object = urllib.urlopen(file)
            reader = csv.reader(file_object)
        except IOError as e:
            print e
            status = False

        j = 0
        if status:
            for row in reader:
                findata[self.key[0]] = row[0]
                findata[self.key[1]] = str(self.CurrentDate)

                for i in range(1,5):
                    try:
                        if row[i] == 'N/A':
                            findata[self.key[i]] = row[i]
                        else:
                            findata[self.key[i]] = round(float(row[i]),3)
                    except ValueError:
                        print 'Yahoo Finance error for {}..'.format(ticker)

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

        return findata


    def sixmonth(self,ticker,date_list):
        #Returns current and previous price for a company based on passed ticker symbol and list of dates
        chng = 'NULL'

        status, prices = get_quotes.download_quotes(ticker, date_list[1], date_list[0])

        if status:
            chng = round(((prices[1]-prices[0])/prices[0])*100,2)
        else:
            print 'No price history for - ' + ticker

        return chng


    def tsx_ticker_list(self):

        query = "Select Symbol from tsx_companies"
        companies = self.dtb.db_fetch(query)

        return companies


    def score_assign(self, data, metric):

        metrics = {'Price/Earnings': 0,
                   'Price/Sales': 0,
                   'Price/Book': 0,
                   'Dividend Yield': 1,
                   'MC/EBITDA': 1,
                   'Six Month Change': 1
                   }

        sample_size = len(data)
        print "scoring " + metric

        for index, company in enumerate(data):

            if company[3] not in [0.0, 'N/A']:
                if key == True:
                    applicable = float(sample_size-index)
                rank = abs((1*metrics[metric]-(sample_size-index)/applicable))*80+20
                key = False

            else:
                rank = 20
                key = True

            if metric == 'Price/Earnings':
                query = "Insert into `rankings` (`Ticker`, `Date`, `Description`, `{0}`) VALUES('{1}', '{2}', '{3}', '{4}')".format(metric,
                                                                                                                                    company[0],
                                                                                                                                    company[1],
                                                                                                                                    company[2],
                                                                                                                                    rank
                                                                                                                                    )
            else:
                query = "UPDATE `rankings` SET `{0}`= '{1}' where `Ticker` = '{2}' AND `Date`= '{3}' AND `Description`= '{4}'".format(metric,
                                                                                                                                   rank,
                                                                                                                                   company[0],
                                                                                                                                   company[1],
                                                                                                                                   company[2]
                                                                                                                                   )
            self.dtb.query_handler(query)


    def sixmonth_score(self, data):

        print 'Scoring Six Month Change'

        sample_size = float(len(data))

        for index, company in enumerate(data):

            rank = (1-(sample_size-index)/sample_size)*100

            query = "UPDATE `rankings` SET `Six Month Change`= '{0}' where `Ticker` = '{1}' AND `Date`= '{2}' AND `Description`= '{3}'".format(rank,
                                                                                                                                   company[0],
                                                                                                                                   company[1],
                                                                                                                                   company[2]
                                                                                                                                   )
            self.dtb.query_handler(query)


            query = "UPDATE `rankings` SET `Six Month Change` = '20' where `Date`= '{2}' AND `Six Month Change` is NULL".format(rank,
                                                                                                                                   company[0],
                                                                                                                                   company[1],
                                                                                                                                   company[2]
                                                                                                                                   )
            self.dtb.query_handler(query)


    def overall_score(self, date):

        print 'tallying overall scores'

        overall_query = "SELECT * from `rankings` where `Date` = '{0}'".format(str(date))
        data = self.dtb.db_fetch(overall_query)

        for company in data:

            score = (sum([float(company[i]) for i in range(5,11)]))/600.0*100

            update_query = "UPDATE `rankings` SET `Overall` = '{0}' where `Ticker`= '{1}' AND `Date`= '{2}'".format(score,
                                                                                                                       company[1],
                                                                                                                       date)
            self.dtb.query_handler(update_query)


    def upload(self,ticker,data_dict):

        query = "INSERT INTO `results_2`(`Ticker`, `Date`,`Description`,`Price/Earnings`, `Price/Sales`, `Price/Book`, `Dividend Yield`, `MC/EBITDA`, `Six Month Change`) VALUES ('"+ ticker[0] +"','" + str(self.CurrentDate)+"','"

        for entry in self.key:
            try:
                query += str(data_dict[entry]) + "','"
            except KeyError:
                query += 'N/A' + "','"

        query += data_dict['Six Month Change'] + "')"
        self.dtb.query_handler(query)


    def data_ranker(self, date):

        base_query = "SELECT `Ticker`, `Date`, `Description`, `{0}` from `results` where `Date` = '{1}' ORDER BY `{2}`"

        metrics = ['Price/Earnings',
                   'Price/Sales',
                   'Price/Book',
                   'Dividend Yield',
                   'MC/EBITDA',
                   ]

        for metric in metrics:

            query = base_query.format(metric, str(date), metric)
            d = self.dtb.db_fetch(query)
            self.score_assign(d, metric)

        # rank 6 month change
        query = "SELECT `Ticker`, `Date`, `Description`, `Six Month Change` FROM `results` where `Six Month Change` <> 0 order by `Six Month Change`"
        d = self. dtb.db_fetch(query)
        self.sixmonth_score(d)

        #tally overall scores
        self.overall_score(date)


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

            if d['Six Month Change'] != 'NULL':
                self.upload(ticker, d)

        #self.data_ranker(self.CurrentDate)



x = trending_value_screen()
x.main()