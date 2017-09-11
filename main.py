from datetime import date
import datetime
import time
from database_interface import database_interface
from date_pricing import historical_pricing
import urllib
import csv
import get_quotes


class trending_value_screen():


    def __init__(self):

        #api_data_fetch variables
        self.StatPage = 'http://finance.yahoo.com/d/quotes.csv?s='
        self.key = ['Description', 'Price/Earnings', 'Price/Sales', 'Price/Book', 'DY', 'EBITDA/MC']

        #six_month variables
        self.BasePage = 'http://finance.yahoo.com/table.csv?s='

        #begin database instance
        self.dtb = database_interface()


    def api_data_fetch(self,ticker):

        findata = {}
        file = self.StatPage + ticker + '&f=' + 'nrp5p6yj1j4'
        status = True
        mc_ebitda = []

        try:
            file_object = urllib.urlopen(file)
            reader = csv.reader(file_object)
        except IOError as e:
            print e
            status = False

        if status:
            for row in reader:
                findata[self.key[0]] = row[0]
                findata[self.key[1]] = str(self.date_obj)

                for i in range(1,5):
                    try:
                        if row[i] == 'N/A':
                            findata[self.key[i]] = row[i]
                        else:
                            findata[self.key[i]] = round(float(row[i]),3)
                    except ValueError:
                        print 'Yahoo Finance error for {}..'.format(ticker)
                    except IndexError:
                        print 'Yahoo Finance API temporary offline'

                # assign EBITDA/MC - higher the better
                # fetch and convert mc to decimal format
                for index in [6, 5]: # 6 - EBITDA, 5 - market cap
                    try:
                        if row[index] not in ['N/A', '0.00']:
                            val = row[index].split('M')
                            if len(val) == 2:
                                val = round(float(val[0])*10**6)
                            else:
                                val = row[5].split('B')
                                val = round(float(val[0])*10**9)

                            mc_ebitda.append(val)

                        else:
                            print 'No EBITDA/mc data for %s' %(ticker)
                    except (IndexError,ValueError):
                        print 'Error' + file

                if len(mc_ebitda) ==2:
                    findata["EBITDA/MC"] = mc_ebitda[0]/mc_ebitda[1]
                else:
                    print "Cannot calculate EBITDA/MC value"
                    findata["EBITDA/MC"] = 0

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

        query = "Select Symbol from tsx_companies_2"
        companies = self.dtb.db_fetch(query)

        print len(companies)

        return companies


    def score_assign(self, data, metric):

        metrics = {'Price/Earnings': 0,
                   'Price/Sales': 0,
                   'Price/Book': 0,
                   'Dividend Yield': 1,
                   'EBITDA/MC': 1,
                   'Six Month Change': 1
                   }

        sample_size = float(len(data))
        print "scoring " + metric

        for index, company in enumerate(data):

            if metric != "EBITDA/MC":

                if company[3] not in [0.0, 'N/A']:
                    if key == True:
                        applicable = float(sample_size-index)
                    rank = abs((1*metrics[metric]-(sample_size-index)/applicable))*80+20
                    key = False

                else:
                    rank = 20
                    key = True

            else:
                rank = abs((1*metrics[metric]-(sample_size-index)/sample_size))*80+20






            if metric == 'Price/Earnings':
                query = "Insert into `rankings_2` (`Ticker`, `Date`, `Description`, `{0}`) VALUES('{1}', '{2}', '{3}', '{4}')".format(metric,
                                                                                                                                    company[0],
                                                                                                                                    company[1],
                                                                                                                                    company[2],
                                                                                                                                    rank
                                                                                                                                    )
            else:
                query = "UPDATE `rankings_2` SET `{0}`= '{1}' where `Ticker` = '{2}' AND `Date`= '{3}' AND `Description`= '{4}'".format(metric,
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

            query = "UPDATE `rankings_2` SET `Six Month Change`= '{0}' where `Ticker` = '{1}' AND `Date`= '{2}' AND `Description`= '{3}'".format(rank,
                                                                                                                                   company[0],
                                                                                                                                   company[1],
                                                                                                                                   company[2]
                                                                                                                                   )
            self.dtb.query_handler(query)


            query = "UPDATE `rankings_2` SET `Six Month Change` = '20' where `Date`= '{2}' AND `Six Month Change` is NULL".format(rank,
                                                                                                                                   company[0],
                                                                                                                                   company[1],
                                                                                                                                   company[2]
                                                                                                                                   )
            self.dtb.query_handler(query)


    def overall_score(self, date):

        print 'tallying overall scores'

        overall_query = "SELECT * from `rankings_2` where `Date` = '{0}'".format(str(date))
        data = self.dtb.db_fetch(overall_query)

        for company in data:

            score = (sum([float(company[i]) for i in range(5,11)]))/600.0*100

            update_query = "UPDATE `rankings_2` SET `Overall` = '{0}' where `Ticker`= '{1}' AND `Date`= '{2}'".format(score,
                                                                                                                       company[1],
                                                                                                                       date)
            self.dtb.query_handler(update_query)


    def upload(self,ticker,data_dict):

        query = "INSERT INTO `results_2`(`Ticker`, `Date`,`Description`,`Price/Earnings`, `Price/Sales`, `Price/Book`, `Dividend Yield`, `EBITDA/MC` , `Six Month Change`) VALUES ('"+ ticker[0] +"','" + str(self.CurrentDate)+"','"

        for entry in self.key:
            try:
                query += str(data_dict[entry]) + "','"
            except KeyError:
                query += 'N/A' + "','"

        query += data_dict['Six Month Change'] + "')"
        self.dtb.query_handler(query)


    def data_ranker(self, date):

        base_query = "SELECT `Ticker`, `Date`, `Description`, `{0}` from `results_2` where `Date` = '{1}' ORDER BY `{2}`"

        metrics = ['Price/Earnings',
                   'Price/Sales',
                   'Price/Book',
                   'Dividend Yield',
                   'EBITDA/MC',
                   ]

        # for metric in metrics:
        #
        #     query = base_query.format(metric, str(date), metric)
        #     d = self.dtb.db_fetch(query)
        #     self.score_assign(d, metric)

        # rank 6 month change
        query = "SELECT `Ticker`, `Date`, `Description`, `Six Month Change` FROM `results_2` where `Date` = '{}' AND `Six Month Change` <> 0 order by `Six Month Change`".format(str(self.CurrentDate))
        d = self.dtb.db_fetch(query)
        self.sixmonth_score(d)

        #tally overall scores
        self.overall_score(str(date))


    def main(self):

        #Determine today's date
        self.CurrentDate = date.today()
        #instantiate historical pricing
        self.hp = historical_pricing()

        #Adjust current date to business day
        self.date_obj = self.hp.CurrentDateAdjustement(self.CurrentDate)
        #Fetch previous date obj
        prev_obj = self.hp.MonthDate(self.date_obj,6)

        l = self.tsx_ticker_list()

        # for ticker in l:
        #
        #     delay = float(str(datetime.datetime.now()).split(":")[2])/10    #millisecond delay to avoid yahoo's anti scraping algorithms (ms)
        #     time.sleep(delay)
        #     d = self.api_data_fetch(ticker[0])
        #     price_change = self.sixmonth(ticker[0],[self.date_obj,prev_obj])
        #     d['Six Month Change'] = str(price_change)
        #
        #     if d['Six Month Change'] != 'NULL':
        #         self.upload(ticker, d)

        self.data_ranker(self.CurrentDate)



if __name__ == "__main__":

    x = trending_value_screen()
    x.main()