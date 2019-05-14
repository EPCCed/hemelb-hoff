from __future__ import print_function
import argparse
from hoff.client import Config, Session

class Column(object):
    def __init__(self, title, data, format_template, formatter=str):
        self.title = title
        self.data = data
        self.string_data = [formatter(item) for item in data]
        self.width = max(len(s) for s in self.string_data)
        self.fmt_str = format_template
    pass

class Printer(object):
    def __init__(self, col_names, data, dest=None):
        self.columns = [Column(name, data[name], self.format_template) for name in col_names]
        self.ncols = len(self.columns)
        self.nrows = len(self.columns[0].data)

        self.header = self.make_line(lambda c : c.fmt_str.format(c.title, width=c.width))
        self.width = len(self.header)
        self.hline = '-'*self.width
        
        if dest is None:
            self.printer = print
        else:
            def p(*objs):
                print(*objs, file=dest)
            self.printer = p

    def __call__(self):
        self.print_header()
        for i in range(self.nrows):
            self.printer(self.make_line(lambda c: c.fmt_str.format(c.data[i], width=c.width)))
        self.print_footer()
    pass

class TablePrinter(Printer):
    format_template = '{: <{width:d}}'
    def make_line(self, getter):
        return '| ' + ' | '.join(getter(c) for c in self.columns) + ' |'

    def print_header(self):
        self.printer(self.hline)
        self.printer(self.header)
        self.printer(self.hline)

    def print_footer(self):
        self.printer(self.hline)

    pass

class PlainPrinter(Printer):
    format_template = '{}'
    def make_line(self, getter):
        return ' '.join(getter(c) for c in self.columns)

    def print_header(self):
        pass
    def print_footer(self):
        pass

    pass

def print_table(col_names, data_by_name):
    columns = [Column(name, data_by_name[name]) for name in col_names]
    # Headers
    ncols = len(columns)
    nrows = len(columns[0].data)

    def make_line(getter):
        return '| ' + ' | '.join(getter(c) for c in columns) + ' |'

    header = make_line(lambda c : c.fmt_str.format(c.title))
    width = len(header)
    hline = '-' * width
    print(hline)
    print(header)
    print(hline)    
    for i in range(nrows):
        print(make_line(lambda c: c.fmt_str.format(c.data[i])))
    print(hline)

def run(args):
    columns = args.cols
    PrinterCls = {
        'table': TablePrinter,
        'plain': PlainPrinter
        }[args.format]
    conf = Config(args.config)

    table = {k: [] for k in columns}
    
    with Session(conf) as s:
        jclient = s.jobs
        jobs = jclient.list()

        for job_id in jobs:
            j = jclient.get(job_id)
            for k in columns:
                table[k].append(getattr(j, k))
    if len(jobs):
        PrinterCls(columns, table)()
