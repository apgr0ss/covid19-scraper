import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

"""
COVID-19 SCRAPE
Author: Andrew Gross

This program:
    - Downloads raw html
    - Scrapes data and
    - Exports as an Excel workbook where each tab contains the
      county-level COVID19 statistics for a given state.

Notes:
1) Must have Chrome installed
2) The path to the Chrome webdriver must be saved in the path environmental
   variable
3) The prefix of the  class names which contain the county and state data seem
   to change occasionally. If this happens (i.e, when the code breaks), inspect
   the webpage again and rename the class using the class_name variable below
"""

# Defines the prefix of the class name -- it changes occasionally
class_name = "jsx-742282485"

# Set options to hide browser window
chrome_options = Options()
#chrome_options.add_argument("--headless")

# Instantiate the driver -- the object that interfaces with Chrome
driver = webdriver.Chrome(options=chrome_options)

# Instruct driver to go to COVID-19 website
driver.get("https://coronavirus.1point3acres.com")

# Expand all of the state collapsables -- these countain the county data
#
# It's a bit of an annoying process -- in order for the driver to
# click to expand a menu, the clickable item must be on the screen.
# I figured out the best way to do this is to expand the list of states
# starting at the bottom and working up.
us_elem = driver.find_elements_by_class_name(class_name + '.row')[0]
elements = driver.find_elements_by_css_selector('div.' + class_name + '.stat.row')


driver.execute_script("arguments[0].scrollIntoView(true);", elements[0])

# Iterate through the elements (states) and click to expand each
for i in range(len(elements)-3,-1,-1):
    driver.execute_script("arguments[0].scrollIntoView(true);", elements[i]);
    elements[i+2].click()

# Pull elements which contain the state and county data
state_elements = driver.find_elements_by_class_name(class_name + '.stat.row.expand')
county_elements = driver.find_elements_by_class_name(class_name + '.counties')


# Define dictionary where
#   keys are state names
#   items are dataframes which have state + county data
master_dict = {}
# Iterate through each state - county group
for state,counties in zip(state_elements,county_elements):
    # Capture and clean state-level data
    state_data = state.get_attribute('innerText') # innerText is the attribute which contains the data

    # Perform basic string operations to pull out the clean data
    state_data = state_data.split('\n')
    state_data = [s.replace('%','') for s in state_data]
    state_data = [s.replace(',','') for s in state_data]
    state_data[0] = state_data[0] + ' (State-level)'

    # Convert numbers to floats
    # Remove the +{number}'s for the state data
    i = 0
    while i < len(state_data):
        s = state_data[i]
        if '+' in s:
            state_data = state_data[:i] + state_data[(i+1):]
            continue
        try:
            state_data[i] = float(s)
            i += 1
        except ValueError:
            i += 1
            continue

    # Capture and clean county-level data
    county_data = counties.get_attribute('innerText')
    county_data = county_data.split('\n')
    county_data = [s.replace('%','') for s in county_data]
    county_data = [s.replace(',','') for s in county_data]
    # Convert numbers to floats
    # Remove the +{number}'s for the county data
    i = 0
    while i < len(county_data):
        s = county_data[i]
        if '+' in s:
            county_data = county_data[:i] + county_data[(i+1):]
            continue
        try:
            county_data[i] = float(s)
            i += 1
        except ValueError:
            i += 1
            continue

    # Build county rows of dataframe
    county_groups = []
    temp_county = []
    for i,s in enumerate(county_data):
        if (type(s) == str) & (i == 0):
            temp_county = [s]
        elif type(s) == str:
            county_groups += [temp_county]
            temp_county = [s]
        else:
            temp_county += [s]
            if i == len(county_data) - 1:
                county_groups += [temp_county]

    # Combine state and county data
    state_county_df = [state_data] + county_groups
    # Extract just the state name (currently state_name + "(State-level)")
    state_name = state_data[0][:-14:1]
    # Create dataframe
    aux_df = pd.DataFrame(state_county_df)
    # Change column names
    aux_df.columns = ['state','confirmed','deaths','fatality_rate (%)']
    # Convert 'confirmed' and 'deaths' columns to integers
    aux_df.confirmed = aux_df.confirmed.astype(int)
    aux_df.deaths = aux_df.deaths.astype(int)
    # Make the state name column the index
    aux_df = aux_df.set_index('state')
    # Save dataframe to the master dictionary
    master_dict[state_name] = aux_df

# Save dataframes to an excel workbook, where each
# tab is the county+state data for a given state
with pd.ExcelWriter('covid_19_by_county.xlsx') as writer:
    for key in master_dict:
        aux_df = master_dict[key]
        aux_df.to_excel(writer, sheet_name=key)

# Close the driver
driver.close()
