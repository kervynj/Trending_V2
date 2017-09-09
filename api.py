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




