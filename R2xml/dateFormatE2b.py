# getting date fomates based on the cioms data
class dateFormatE2b:
    def get_month_number(self):
        if self.key in self.calender:

            return self.calender[self.key]
        else:
            return 0

    def __init__(self, key):
        self.calender = {}
        self.calender = self.calender.fromkeys(["JAN", "JANUARY", "01", "1"], "01")
        self.calender.update(self.calender.fromkeys(["FEB", "FEBRUARY", "02", "2"], "02"))
        self.calender.update(self.calender.fromkeys(["MAR", "MARCH", "03", "3"], "03"))
        self.calender.update(self.calender.fromkeys(["APR", "APRIL", "04", "4"], "04"))
        self.calender.update(self.calender.fromkeys(["MAY", "May", "05", "5"], "05"))
        self.calender.update(self.calender.fromkeys(["JUN", "JUNE", "06", "6"], "06"))
        self.calender.update(self.calender.fromkeys(["JUL", "JULY", "07", "7"], "07"))
        self.calender.update(self.calender.fromkeys(["AUG", "AUGUST", "08", "8"], "08"))
        self.calender.update(self.calender.fromkeys(["SEP", "SEPTEMBER", "09", "9"], "09"))
        self.calender.update(self.calender.fromkeys(["OCT", "OCTOBER", "10"], "10"))
        self.calender.update(self.calender.fromkeys(["NOV", "NOVEMBER", "11"], "11"))
        self.calender.update(self.calender.fromkeys(["DEC", "DECEMBER", "12"], "12"))
        self.key = key.upper()
