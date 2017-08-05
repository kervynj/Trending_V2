from datetime import date,datetime, timedelta



class historical_pricing:

    def __init__(self):
        self.m = [[0,31],[1,28],[2,31],[3,30],[4,31],[5,30],[6,31],[7,31],[8,30],[9,31],[10,30],[11,31]]

    def DateAdjustment(self,Date):

        dobj = Date
        RefWeekDay = dobj.weekday()
        RefDay = dobj.day
        RefMonth = dobj.month
        RefYear = dobj.year

        #Check if Reference week day is a business day
        if RefWeekDay > 4:
            if (RefDay + (4 - (RefWeekDay))) < 1:
                RefDay = self.m[(RefMonth-2)][1] + (RefDay + (4 - int(RefWeekDay)))
                RefMonth -= 1
            else:
                RefDay += (4 - int(RefWeekDay))

        self.Previous_Day = RefDay
        self.Previous_Year = RefYear
        self.Previous_Month = RefMonth
        self.Previous_Date_obj = date(RefYear,RefMonth,RefDay)
        return self.Previous_Date_obj


    def MonthDate(self,Date,key):

        SixDateobj = Date
        Year = SixDateobj.year
        Month = SixDateobj.month - key
        Day = SixDateobj.day

        try:
            SixDateobj = date(Year,Month,Day)
        except ValueError:
            if SixDateobj.month < key:
                Month = 12 + (SixDateobj.month-key)
                Year -=1
            try:
                SixDateobj = date(Year,Month,Day)
            except ValueError:
                if Day > self.m[Month-1][1]:
                    Day = self.m[Month-1][1]


        SixDateobj = self.DateAdjustment(date(Year,Month,Day))
        return SixDateobj


    def price_array(self,CurrentDate,PreviousDate,Ticker):

        yesterdate = CurrentDate - timedelta(days=1)
        yesterdate = self.DateAdjustment(yesterdate)
        CurrentYear = yesterdate.year
        CurrentMonth = yesterdate.month
        Yesterday = yesterdate.day

        BasePage = 'http://real-chart.finance.yahoo.com/table.csv?s='
        YesterdayObj = self.DateAdjustment(date(CurrentYear,CurrentMonth,Yesterday))

        #Create URL to fetch price changes
        file = BasePage + Ticker +'&d='+ str(YesterdayObj.month-1)+'&e='+str(YesterdayObj.day)+'&f='+str(YesterdayObj.year)+'&g=d&a='+str(PreviousDate.month -1)+'&b='+ str(PreviousDate.day)+ '&c=' + str(PreviousDate.year) + '&ignore=.csv'
        file_object = urllib.urlopen(file)
        pricereader = csv.DictReader(file_object)
        info = {}

        for row in pricereader:
            try:
                info[row['Date']]= [(float(row['Adj Close']))]
            except KeyError:
                pass
            try:
                day_change = 100*(float(row['Adj Close']) - float(row['Open']))/(float(row['Open']))
            except KeyError:
                continue

            info[row['Date']].append(day_change)

        return info


    def change_array(self,o_dict):

        for w in o_dict:

            y = w.split('-')
            yesterday = (date(int(y[0]),int(y[1]),int(y[2]))-timedelta(days=1))
            yesterday = str(self.DateAdjustment(yesterday))

            try:
                chng = 100*(o_dict[w][0]-o_dict[yesterday][0])/o_dict[yesterday][0]
            except KeyError:
                chng = 0
            try:
                o_dict[w].append(chng)
            except UnboundLocalError:
                pass

        return o_dict