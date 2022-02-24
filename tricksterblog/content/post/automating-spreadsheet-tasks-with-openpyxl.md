+++
author = "rl1987"
title = "Automating spreadsheet tasks with openpyxl"
date = "2022-12-24"
tags = ["automation", "python", "openpyxl"]
+++

Spreadsheets are a mainstay tool for information processing in many domains and widely used by people in many walks
of life. It is fairly common for developers working in scraping and automation to be dealing with spreadsheets for
inputting data into custom code, report generation and other tasks. [Openpyxl](https://foss.heptapod.net/openpyxl/openpyxl)
is a prominent Python module for reading and writing a spreadsheet files in Open Office XML format that is compatible
with many spreasheet programs (MS Excel 2010 and later, Google Docs, Open Office, Libre Office, Apple Numbers, etc.).

First, let us download a spreadsheet file for experimentation. In this example we are going to read medical service pricing
data for a certain hospital in USA.

```
$ wget https://28g1xh366uy0x9ort41hns72-wpengine.netdna-ssl.com/wp-content/uploads/2021/12/Albuquerque-Price-Transparency-01-2022.xlsx
```

Spreadsheet document is opened into workbook (openpyxl object for entire spreadsheet document) by calling `load_workbook()` function:

```
>>> import openpyxl
>>> wb = openpyxl.load_workbook("Albuquerque-Price-Transparency-01-2022.xlsx")
```

Argument to `load_workbook()` can also be a file handle or some object similar to it (e.g. `BytesIO` buffer from `io` module).

Now we need to get a work sheet object for a primary (active) sheet. We can get it by reading `active` property of the work book.

```
>>> ws = wb.active
>>> ws
<Worksheet "Albuquerque Jan 2019">
```

We may want to read other sheets as well, or read a certain sheet by it's name. For this purpose, `sheetnames` property 
provides a list of names of individual sheets in the document:

```
>>> wb.sheetnames
['Albuquerque Jan 2019']
```

Indexing work book object by a sheet name gives a work sheet object for that sheet, or raises an exception if it does not
exist:

```
>>> wb['Albuquerque Jan 2019']
<Worksheet "Albuquerque Jan 2019">
>>> wb['...']
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/local/lib/python3.9/site-packages/openpyxl/workbook/workbook.py", line 288, in __getitem__
    raise KeyError("Worksheet {0} does not exist.".format(key))
KeyError: 'Worksheet ... does not exist.'
```

One way to read data from work sheet is to get individual cells (by row and column) and access their `value` property:

```
>>> ws.cell(row=1, column=1)
<Cell 'Albuquerque Jan 2019'.A1>
>>> ws.cell(row=1, column=1).value
'Albuquerque'
```

Note that row and column indices start at 1, not at 0.

Another way is to use row generator at `rows` property that will lazily read and return lists of cells on a give work sheet.
Iterating across `rows` is an easy way to get all data within the work sheet:

```
>>> for row in ws.rows:
...     row = list(map(lambda cell: cell.value, row))
...     print(row)
... 
['Albuquerque', None, None, None]
['Revenue Code', 'Description', 'Procedure Number', 'Standard Amount']
[111, 'PRIVATE ROOM - LTAC', 'PRVL', 1750]
[118, 'PRIVATE ROOM - REHAB', 'PRIVR', 1345]
[121, 'SEMI-PRIVATE ROOM LTAC', 'SEMIL', 1750]
[128, 'SEMI-PRIVATE ROOM REHAB', 'SEMIR', 13.45]
[190, 'PRIVATE ROOM SUB-ACUTE', 'PRSUB', 1200]
[190, 'SEMI-PRIVATE ROOM SUB-ACUTE', 'SEMSUB', 1200]
[202, 'ICU ROOM PRIVATE', 'ICUP', 2135]
...
```

Now let us create a new workbook object to exemplify ways of writing data into spreadsheets through openpyxl:

```
>>> wb = openpyxl.Workbook()
>>> wb
<openpyxl.workbook.workbook.Workbook object at 0x116f93190>
```

Like with Excel, this newly created work book comes with a single empty work sheet:

```
>>> wb.sheetnames
['Sheet']
>>> ws = wb.active
>>> ws
<Worksheet "Sheet">
```

One way set value of a cell is to use indexing with Excel notation:

```
>>> ws['A1'] = 'N'
>>> ws['A2'] = 25
>>> ws['A1']
<Cell 'Sheet'.A1>
>>> ws['A1'].value
'N'
>>> ws['A2'].value
25
```

Another way is to call `cell` method on work sheet object with `value` keyword argument being set:

```
>>> _ = ws.cell(row=2, column=1, value='x')
>>> _ = ws.cell(row=2, column=2, value=3.5)
```

If you want to append an entire row (e.g. when doing row-by-row writing of scraped data) you can call `append()`
method on work sheet:

```
>>> ws.append(['f', 8000])
```

Note that cell values can also be formulas that spreadsheet programs will run once.

We may want to add new work sheet to a workbook. This can be done by calling `create_sheet()` method with name of new sheet:

```
>>> wb.create_sheet('test')
<Worksheet "test">
>>> wb.sheetnames
['Sheet', 'test']
```

To delete a sheet, we use the `del` operator on it:

```
>>> del wb['test']
>>> wb.sheetnames
['Sheet']
```

Calling `save()` method on a workbook with path of output XLSX file will save it to a file and write out all contents from the
memory.

Openpyxl also allows us to control visual style of cells (fonts, colors, borders, cell alignments. See
[Working with styles](https://openpyxl.readthedocs.io/en/stable/styles.html) page of the official documentation.

If you are automating spreadsheet tasks with Python, you may also want to check out the following modules:

* [Pandas](https://pandas.pydata.org/) - Swiss army knife for handling tabular data across multiple formats including, 
but not limited to, spreadsheets. Think of it as a more programmable version of Excel inside Python module.
* [XlsxWriter](https://xlsxwriter.readthedocs.io/) - Python module for writing data to older format that is compatible with
Excel 2007+.
* [xlrd](https://github.com/python-excel/xlrd) - Python module for reading legacy .xls files.
* [Google client libraries for Google Sheets/Drive/Docs](https://developers.google.com/sheets/api/quickstart/python)
