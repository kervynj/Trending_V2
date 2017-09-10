# service routines necessary required for GUI widgets
# layering :  top - GUI
#             middle - api
#             lowest - main

import main

class api(object):

    def connect(self):
        self.trendingvalue = main.trending_value_screen()
        self.dtb = self.trendingvalue.dtb


    def dates(self):

        query = "SELECT DISTINCT Date from rankings_2"
        date_list = self.dtb.db_fetch(query)

        return date_list


    def screener_results(self, date):


        query = """ SELECT `Ticker`, `Description`, `Overall` from `rankings_2`
                    where Date = '{}'
                    ORDER BY `rankings_2`.`Overall`  DESC
                    Limit 20""".format(date)

        companies = self.dtb.db_fetch(query)
        return companies

    def company_financials(self, ticker, date):

        query = "Select `Price/Earnings`, `Price/Sales`, `Price/Book`, `Dividend Yield`, `EBITDA/MC`, `Six Month Change`" \
                "from `results_2` where `Ticker` = '{0}' AND `Date` = '{1}'".format(ticker, date)

        info = self.dtb.db_fetch(query)

        return info




