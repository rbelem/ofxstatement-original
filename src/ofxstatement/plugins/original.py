import csv
from datetime import datetime
from decimal import Decimal

from ofxstatement.plugin import Plugin
from ofxstatement.parser import StatementParser
from ofxstatement.statement import Statement, StatementLine

MONTH_MAP = {
    'Jan': 'Jan',
    'Fev': 'Feb',
    'Mar': 'Mar',
    'Abr': 'Apr',
    'Mai': 'May',
    'Jun': 'Jun',
    'Jul': 'Jul',
    'Ago': 'Aug',
    'Set': 'Sep',
    'Out': 'Oct',
    'Nov': 'Nov',
    'Dez': 'Dec',
}

class BancoOriginalPlugin(Plugin):
    """BancoOriginal plugin
    """

    def get_parser(self, filename):
        return BancoOriginalParser(filename, self.settings)


class BancoOriginalParser(StatementParser):
    date_format = "%d/%b"

    mappings = {
        'date': 0,
        'memo': 1,
        'trntype': 2,
        'amount': 3,
    }

    def __init__(self, filename, settings):
        self.fin = filename
        self.settings = settings
        self.statement = Statement(bank_id='0212', currency='BRL')

        self.statement.acct_id = self.settings.get("account"),
        self.statement.branch_id = '1'

    def parse(self):
        with open(self.fin, 'r',
                  encoding=self.settings.get("charset", "ISO-8859-1")) as f:
            self.fin = f
            reader = self.split_records()
            for line in reader:
                self.cur_record += 1
                if not line:
                    continue
                if self.cur_record == 1:
                    continue
                stmt_line = self.parse_record(line)
                if stmt_line:
                    stmt_line.assert_valid()
                    self.statement.lines.append(stmt_line)

        return self.statement

    def parse_value(self, value, field):
        tp = type(getattr(StatementLine, field))
        if tp == datetime:
            return self.parse_datetime(value)
        elif tp == Decimal:
            return self.parse_decimal(value)
        elif field == 'trntype':
            return self.parse_trntype(value)
        else:
            return value

    def parse_datetime(self, value):
        day, month_pt_br = value.split('/')
        new_value = '{}/{}'.format(day, MONTH_MAP[month_pt_br])
        date = datetime.strptime(new_value, self.date_format)
        now = datetime.today()
        # TODO: Add a config setting for start/end date
        date = date.replace(year=self.settings.get("year", now.year))
        return date

    def parse_decimal(self, value):
        new_value = value.replace('R$', '')
        new_value = new_value.replace(' ', '')
        new_value = new_value.replace('.', '')
        new_value = new_value.replace(',', '.')
        return Decimal(new_value)

    def parse_trntype(self, value):
        if value == 'Débito':
            return 'DEBIT'
        elif value == 'Crédito':
            return 'CREDIT'

    def split_records(self):
        return csv.reader(self.fin, delimiter=';')

    def parse_record(self, line):
        stmt_line = StatementLine()
        for field, col in self.mappings.items():
            if col >= len(line):
                raise ValueError("Cannot find column %s in line of %s items "
                                 % (col, len(line)))
            rawvalue = line[col]
            value = self.parse_value(rawvalue, field)
            setattr(stmt_line, field, value)
        return stmt_line
