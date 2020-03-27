# COVID-19 Scraper

Scrapes the state and county-level COVID-19 data from [here](https://coronavirus.1point3acres.com)

This program:
- Downloads raw html
- Scrapes data and
- Exports as an Excel workbook where each tab contains the
  county-level COVID-19 statistics for a given state.

`run_scraper.sh` is intended to be executed by a task scheduler, so the Excel workbook is automatically updated on a frequent basis.

## Notes:
1. The program assumes you have Chrome (otherwise, install the web driver for your desired browser [here](https://selenium-python.readthedocs.io/installation.html#))
2. This program assumes the path to the webdriver must be saved in the path environmental
   variable
3. The prefix of the class names which contain the county and state data seem
   to change occasionally. If this happens (i.e, when the code breaks), inspect
   the webpage again and rename the class using the class_name variable
