#!/usr/bin/python
from  Tkinter import *
import tkMessageBox
from api import api


class trending_GUI(object):

    def __init__(self):

        self.root = Tk()
        self.root.title("Trending Value V2.0")
        self.service = api()
        
        self.leftframe = Frame(self.root)
        self.leftframe.pack(side=LEFT, expand=True)
        self.rightframe = Frame(self.root)
        self.rightframe.pack(side=RIGHT)
        
        self.messagebarset()
        self.buttonset()
        self.date_scroll = Listbox(self.leftframe, height='2')
        self.date_scroll.grid(row=2, column=0, columnspan=3)
        self.datascroll = Listbox(self.rightframe, width="50")
        self.datascroll.pack()
        self.get_info_button = Button(self.rightframe, text="Get Info", command=self.getInfo)
        self.get_info_button.pack(side=BOTTOM)

        self.root.mainloop()

        
    def buttonset(self):

        connect_button = Button(self.leftframe, text ='Connect to Service', fg='Red', command=self.connect)
        connect_button.grid(row=1, column=1, columnspan=1)

        datafetch_button = Button(self.leftframe, text="Fetch Data", command=self.display_screener_results)
        datafetch_button.grid(row=3, column=1, columnspan = 1)


    def messagebarset(self):

        self.textbox = Text(self.leftframe, height='2', width='50', fg='Blue')
        self.textbox.grid(row=0, column=0, columnspan=3)


    def connect(self):

        try:
            
            if self.service.dtb:
                self.textbox.insert(INSERT, "Already Connected!\n")
        except AttributeError:

            self.service.connect()
            self.dates = self.service.dates()

            for index, d in enumerate(self.dates):
                self.date_scroll.insert(index, d)

            self.selectedDate = str(d)

            self.textbox.insert(INSERT, "Successfully Connected to Service\n")


    def display_screener_results(self):

        self.clear()

        try:
            self.selectedDate = self.dates[self.date_scroll.curselection()[0]][0]
        except IndexError:
            tkMessageBox.showinfo("Error!", "Please select a date \n from the options list")

        stockData = self.service.screener_results(self.selectedDate)

        for index, company in enumerate(stockData):

            basetext = ""

            for entry in company:
                try:
                    entry = round(float(entry),1)
                except ValueError:
                    pass

                basetext += str(entry) + " "

            self.datascroll.insert(index, basetext)

        self.textbox.insert(INSERT, "Success!\n")

    def getInfo(self):

        try:

            line = self.datascroll.get(self.datascroll.curselection())
            ticker = line.split(" ")[0]

            date = self.date_scroll.get(0)[0]

            info = self.service.company_financials(ticker, date)[0]
        except TclError:
            tkMessageBox.showinfo("Error!", "Select an option from the listbox")

        basetext = """\tTicker - {0}
                      P/E: {1}
                      P/S: {2}
                      P/B: {3}
                      DY:  {4}
                      EBITDA/MC: {5}
                      6 month Change: {6}
                   """



        tkMessageBox.showinfo("Company Info", basetext.format(ticker,
                                                              info[0],
                                                              info[1],
                                                              info[2],
                                                              info[3],
                                                              info[4],
                                                              info[5]))



    def clear(self):
        
        length = self.datascroll.size()
        self.datascroll.delete(0, length-1)


if __name__ == "__main__":

    trending_GUI()
