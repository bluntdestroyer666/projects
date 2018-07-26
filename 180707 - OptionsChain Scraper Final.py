
import json
import pandas as pd
import time
import datetime
from pandas.io.json import json_normalize
import os

# Get default JSON results for the symbol you want

symbol_list = ['SPY', 'QQQ', 'XLF', 'NFLX', 'AAPL', 'AMZN', 'GOOG', 'FB', 'EEM', 'AMD', 'IQ', 'MU', 'FXI', 'VXX', 'F', 'EWZ', 'GLD', 'SLV', 'USO', 'TLT']

# Short dummy symbol list (for testing)
#symbol_list = ['FB', 'IQ']

# Make url from yf url + symbol
url = 'https://query2.finance.yahoo.com/v7/finance/options/'

# Today's date (for path)
now = datetime.datetime.now()
timestamp = now.strftime("%Y%m%d")

# Path to write .csv results to. Timestamp makes a new file to organize results by day.
path = 'C:\\Users\\samn\\Documents\\PY\\YF_Scraper_Results\\' + timestamp + '\\'

os.makedirs(path)

# Start the master loop (gets expiry data for symbol, to reference for call/put chains)

for sym in symbol_list:
    
    # Makes new URL
    newurl = url + sym
    
    # Gets JSON
    df = pd.read_json(newurl)
    
    # Gets list of expiry dates (in unix time)
    exp = json_normalize(data=df['optionChain']['result'], record_path='expirationDates')
    
    # Temp lists for our results
    optionschain = []
    
    # A loop to get URLs + expiry dates and pull put/call data
    for date in exp[0]:
        
        # Makes new URL with the symbol URL and expiry date
        newurl2 = newurl + '?date=' + str(date)
        
        # Temporary df's for our shit, written to different df later for output
        temp_df = pd.read_json(newurl2)
        
        chain = json_normalize(data=temp_df['optionChain']['result'], record_path='options')
        
        for j in chain.calls[0]:
            
            j.update({'type': 'call'})
            optionschain.append(j)
       
        for k in chain.puts[0]:
            
            k.update({'type': 'put'})
            optionschain.append(k)
            
        oc_df = pd.DataFrame(optionschain)
        
    ### DTE for expiry dates ###

    exp_dte = []
        
    # Time vars for our loops
    
    today = time.time()
    today_h = datetime.datetime.fromtimestamp(int(today)).strftime('%Y-%m-%d %H:%M:%S')
        
    # Adds DTE to calls df
        
    ### To do: just fucking put calls and puts together, run this all at once. ###

    for l in range(len(oc_df)):

        exp_h = datetime.datetime.fromtimestamp(int(oc_df['expiration'].loc[l])).strftime('%Y-%m-%d %H:%M:%S')

        today_d = datetime.datetime.strptime(today_h, "%Y-%m-%d %H:%M:%S")
        exp_d = datetime.datetime.strptime(exp_h, "%Y-%m-%d %H:%M:%S")

        dte = abs(exp_d - today_d).days
    
        exp_dte.append(dte)
    
    oc_df['dte'] = exp_dte
        
    # Adds human expiration time to puts and calls

    for i in range(len(oc_df)):
        oc_df.loc[i, 'human_time'] = datetime.datetime.fromtimestamp(int(oc_df.loc[i, 'expiration'])).strftime('%Y-%m-%d %H:%M:%S')
        
    # Write to .csv
    oc_df.to_csv(path + sym + '_' + timestamp + '.csv')
        

