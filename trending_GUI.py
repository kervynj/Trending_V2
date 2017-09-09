from  Tkinter import *
import tkMessageBox
#!/usr/bin/python
from api import api

class trending_GUI(object):

    def __init__(self):

        self.root = Tk()
        self.root.title("Trending Value V2.0")
        self.service = api()
        self.frameset()
        self.messagebarset()
        self.buttonset()
        self.root.mainloop()


    def frameset(self):

        self.leftframe = Frame(self.root)
        self.leftframe.pack(side = LEFT, expand = True)
        self.rightframe = Frame(self.root)
        self.rightframe.pack(side = RIGHT)


    def buttonset(self):

        connectbutton = Button(self.leftframe, text ='Connect to Service', fg='Red', command=self.connect)
        connectbutton.grid(row=1, column=1, columnspan=1)

        self.datescroll = Listbox(self.leftframe, height='2')
        self.datescroll.grid(row=2, column=0, columnspan=3)

        datafetch_button = Button(self.leftframe, text="Fetch Data", command=self.display_screener_results)
        datafetch_button.grid(row=3, column=1, columnspan = 1)

        self.datascroll = Listbox(self.rightframe, width="50")
        self.datascroll.pack()


    def messagebarset(self):

        self.textbox = Text(self.leftframe, height='2', width='50')
        self.textbox.grid(row=0, column=0, columnspan=3)


    def connect(self):

        try:
            if self.service.dtb:
                self.textbox.insert(INSERT, "Already Connected!\n")


        except AttributeError:

            self.service.connect()
            self.dates = self.service.dates()

            for index, d in enumerate(self.dates):
                self.datescroll.insert(index, d)

            self.selectedDate = str(d)

            self.textbox.insert(INSERT, "Successfully Connected to Service\n")


    def display_screener_results(self):

        length = self.datascroll.size()
        self.datascroll.delete(0, length-1)

        try:
            self.selectedDate = self.dates[self.datescroll.curselection()[0]][0]
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


if __name__ == "__main__":

    trending_GUI()
