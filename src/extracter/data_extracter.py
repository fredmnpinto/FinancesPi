import errno
import os
import sys
from pprint import pprint

class Extract:
    def __init__(self, txt_path):
        self.txt_path = str(txt_path)
        self.file_name = txt_path.split('/')[len(txt_path.split('/')) - 1]
        csv_name = self.file_name.split('.')[0] + '.csv'
        self.csv_path = f"{os.getenv('CSV_PATH')}/{csv_name}"
        self.initial_balance = None
        self.movements = []
        # Check if the file path is valid
        if not os.path.isfile(txt_path):
            print(f"{txt_path} is not a valid file path")
            exit(-1)
        with open(txt_path) as fr:
            full_str = fr.read()
            fr.close()

        # Clean whitespace off the string list
        self.txt_lines = full_str.split("\n")

        # The first position will allways be the date of the extract
        date_str = rem_whitespace(self.txt_lines[0].split("  "))[0]
        self.date = Date(date_str, "yyyy/mm/dd")

        # Get the initial balance
        self.get_initial_balance()

        # Get the movements
        self.get_movement_lines()

    # Set a custom csv_path
    def set_csv_path(self, new_path):
        self.csv_path = new_path

    # Get the initial balance for that month
    def get_initial_balance(self):
        if self.initial_balance is None:
            for line in self.txt_lines:
                if 'SALDO INICIAL' in line:
                    self.initial_balance = float(rem_whitespace(line)[2])
                    break
            return self.initial_balance

    # Scrap all the lines of the file for the ones with the money movements
    def get_movement_lines(self):
        if self.movements:
            return self.movements
        self.movements = []
        last_balance = self.initial_balance
        for line in self.txt_lines:
            possible_line = rem_whitespace(str(line).split("        "))

            # if like this --> 7.01,7.01,"DD LU96000000 PayPal (Europe) 5HPJ224YL66GN",42.99,5.74
            if len(possible_line) == 3 and are_there_n_numbers_upfront(possible_line[0], 2):
                actual_date, effective_date = get_first_n_nums(possible_line[0], 2)
                actual_date = Date(f'{int(float(actual_date))}/{int(float(actual_date) - int(float(actual_date))) + 1}/{self.date.year}', "dd/mm/yyyy")
                effective_date = Date(f'{int(float(effective_date))}/{int(float(effective_date) - int(float(effective_date))) + 1}/{self.date.year}', "dd/mm/yyyy")
                remaining_balance = float(get_first_num(possible_line[2]))
                actual_amount = remaining_balance - last_balance
                self.movements.append(Movement(actual_date, effective_date, remove_first_n_words(possible_line[0], 2), actual_amount, remaining_balance))
                last_balance = remaining_balance

        return self.movements

    def __repr__(self):
        return f"Extract '{self.date}' - Initial Balance: {'{:.2f}'.format(self.initial_balance)} - {len(self.movements)} movements"

    def save_to_csv(self):
        with open(self.csv_path, 'w') as fw:
            for m in self.movements:
                fw.write(m.to_csv_line() + '\n')
            fw.close()

# Money movements. I.e ->              7.01,7.01,"DD LU96000000 PayPal (Europe) 5HPJ224YL66GN",42.99,5.74
class Movement:
    def __init__(self, actual_date, effective_date, desc, amount, remaining_balance):
        self.amount = float(amount)
        self.remaining_balance = float(remaining_balance)
        self.desc = remove_comma(str(desc))
        self.actual_date = actual_date
        self.effective_date = effective_date

    def __repr__(self):
        return f"Amount: {'{:.2f}'.format(self.amount)}, Remaining Balance: {self.remaining_balance}, Description: {self.desc}"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all([self.amount == other.amount, self.desc == other.desc,
                    self.actual_date == other.actual_date, self.effective_date == other.effective_date,
                    self.remaining_balance == other.remaining_balance])

    def to_csv_line(self):
        return f"{self.actual_date},{self.effective_date},\"{self.desc}\",{'{:.2f}'.format(self.amount)},{self.remaining_balance}"

    def __str__(self):
        return f"{self.actual_date},{self.effective_date},\"{self.desc}\",{'{:.2f}'.format(self.amount)},{self.remaining_balance}"

""" Date i.e -> 22/05/2001 """
class Date:
    def __init__(self, date_str, form):
        if str(form).lower() == "dd/mm/yyyy":
            self.day, self.month, self.year = str(date_str).split('/')
            self.day = int(self.day)
            self.month = int(self.month)
            self.year = int(self.year)
        elif str(form).lower() == "yyyy/mm/dd":
            self.year, self.month, self.day = str(date_str).split('/')
            self.day = int(self.day)
            self.month = int(self.month)
            self.year = int(self.year)

        if self.year < 99:
            self.year = int(f"20{str(self.year)}")

    def __cmp__(self, other):
        if not isinstance(other, Date):
            return None
        dY = self.year - other.year
        dM = self.month - other.month
        dD = self.day - other.day

        if dY != 0:
            return dY
        if dM != 0:
            return dM
        return dD

    @staticmethod
    def _format_num_to_date(num):
        if int(num) < 10:
            return '0' + str(num)
        return num

    def __repr__(self):
        return f"{Date._format_num_to_date(self.day)}/{Date._format_num_to_date(self.month)}/{Date._format_num_to_date(self.year)}"

    def is_before(self, that):
        if not isinstance(that, Date):
            return None
        if self.year < that.year:
            return True
        if self.month < that.month:
            return True
        if self.day < that.day:
            return True
        return False

    def is_after(self, that):
        return not self.is_before(that)

    def to_sql_format(self):
        return f"{self._format_num_to_date(self.year)}{self._format_num_to_date(self.month)}{self._format_num_to_date(self.day)}"

# Remove whitespaces from a list or string
def rem_whitespace(param):
    if isinstance(param, list):
        cpy = []
        for s in param:
            if not any([s == "", s == '', s == ' ', s.isspace()]):
                cpy.append(s)
        return cpy
    if isinstance(param, str):
        cpy = param.split()
        return rem_whitespace(cpy)

    raise errno.EINVAL

# Fetch the first number to appear on a string
def get_first_num(string):
    string = str(string)
    num = ""
    for c in string:
        if is_int(c) or c == '.':
            num += c
        elif len(num) > 0:
            if '.' in num:
                return float(num)
            else:
                return int(num)
    if is_num(num):
        return float(num)

# Return the first integer value inside of given string
def get_first_int(string):
    string = str(string)
    num = ""
    for c in string:
        if is_int(c):
            num += c
        elif len(num) > 0:
            if '.' in num:
                return float(num)
            else:
                return int(num)

# Fetch the first N numbers to appear on a given String
def get_first_n_nums(string, n):
    if n <= 0:
        return None
    n = int(n)
    string = str(string)
    nums = []
    for s in rem_whitespace(string.split(' ')):
        if is_num(s):
            nums.append(s)
            if len(nums) >= n:
                return nums

# Get the first N integers inside of given string
def get_first_n_ints(string, n):
    if n <= 0:
        return None
    n = int(n)
    string = str(string)
    nums = []
    for s in rem_whitespace(string.split(' ')):
        if is_int(s):
            nums.append(s)
            if len(nums) >= n:
                return nums

# Check if there are N numbers to appear before other characters
def are_there_n_numbers_upfront(string, n):
    if n <= 0:
        return None
    n = int(n)
    if isinstance(string, str):
        for s in rem_whitespace(string.split(' ')):
            if is_num(s):
                n -= 1
                if n <= 0:
                    return True
            else:
                return False
    if isinstance(string, list):
        for s in rem_whitespace(string):
            if is_num(s):
                n -= 1
                if n <= 0:
                    return True
            else:
                return False

# Check if given number is parsable integer
def is_int(num):
    try:
        int(num)
        return True
    except Exception:
        return False

# Check if given number is parsable to float
def is_float(num):
    try:
        float(num)
        return True
    except Exception:
        return False

# Check if given string is a number
def is_num(num):
    return is_int(num) or is_float(num)

# Check if the given numbers are parsable to float
def are_floats(num):
    for n in num:
        if not is_float(n):
            return False
    return True

# Remove the first N words from a given string
def remove_first_n_words(string, N):
    str_lst = rem_whitespace(string)
    str_lst.reverse()
    i = 0
    while i < N:
        i += 1
        str_lst.pop()
    str_lst.reverse()
    return str.join(" ", str_lst)

def remove_comma(msg):
    cpy = ""
    for c in msg:
        if c != ',':
            cpy += c
    return cpy

if __name__ == '__main__':
    e = Extract("../../data/txt/EXTRATO COMBINADO 202000317317375871cb66d.txt")
    e.set_csv_path("../data/csv/TESTE.csv")
    pprint(e)
    pprint(e.movements)
    e.save_to_csv()