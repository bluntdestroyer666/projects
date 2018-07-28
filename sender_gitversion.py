
### Make the charts

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import json
from pandas.io.json import json_normalize

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import os
import shutil

# Replace this with scrapers for top IV, top vol, and earnings.

#symbol_list = ['SPY', 'FB', 'AAPL', 'AMZN', 'NFLX', 'GOOG', 'IQ', 'TSLA', 'TLT', 'GLD', 'SLV']
symbol_list = ['TLT', 'FXI']

url = 'https://query2.finance.yahoo.com/v7/finance/options/'

timestamp = datetime.datetime.now().strftime('%Y%m%d')

path = 'temp/'

try:
    os.makedirs(path)

except FileExistsError:
    pass

# Gets the third friday exp

def is_third_friday(s):
    d = datetime.datetime.strptime(s, '%Y-%m-%d')
    return d.weekday() == 3 and 15 <= d.day <= 21

# Gets expiration dates (in unix), converts to human time, gets the first weekly and two monthly dates, gets unix/human time for those.

def date_lister(symbol, exp):

    # Find better way to put unix and human dates together, reference the three dates you want.

    global dates_list

    # Make df for unix and human exp dates

    exp_df = pd.DataFrame()
    exp_df['unix'] = exp[0].values

    # Get human values for exp_df

    ht_list = []

    for i in exp[0]:

        ht = datetime.datetime.fromtimestamp(int(i)).strftime('%Y-%m-%d')
        ht_list.append(ht)

    exp_df['human'] = ht_list

    # Get your nonweekly dates

    non_weeklies = []

    for date in ht_list:
        if is_third_friday(date) == True:
            non_weeklies.append(date)

        else:
            pass

    # Make list with first weekly and two nonweeklies, with unix and human time format

    dates_list = []

    dates_list.append(ht_list[0])

    for i in non_weeklies[:2]:
        dates_list.append(i)

    dates_list = pd.DataFrame(data = dates_list, columns = ['human'])

    dates_list['unix'] = [(exp_df.loc[exp_df['human'] == i, 'unix'].values[0]) for i in dates_list['human']]

def scraper(symbol):

    print('...scraping ' + symbol + ' (' + str(symbol_list.index(symbol) + 1) + '/' + str(len(symbol_list)) + ')')

    global oc_df

    optionschain = []

    for date in dates_list['unix']:

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

        #print(oc_df)

    ### Add mid, add DTE ###

    oc_df['mid'] = (oc_df['bid'] + oc_df['ask'] / 2)

    for i in range(len(oc_df)):
        oc_df.loc[i, 'human'] = datetime.datetime.fromtimestamp(int(oc_df.loc[i, 'expiration'])).strftime('%Y-%m-%d')
        oc_df.loc[i, 'dte'] = (datetime.datetime.strptime(oc_df.loc[i, 'human'], '%Y-%m-%d') - datetime.datetime.now()).days

def graph(symbol):

    # Figure out how to graph bid/ask together here

    print('...graphing ' + symbol + ' (' + str(symbol_list.index(symbol) + 1) + '/' + str(len(symbol_list)) + ')')

    for j in ['bid', 'impliedVolatility']:

        plt.figure(figsize = (20,10))

        colors = np.linspace(1, .25, len(dates_list))

        #print(str(symbol) + ' ' + str(j))

        for i, k in zip(dates_list['human'], colors):

            iv = oc_df[oc_df['human'] == i]

            iv_put = iv[iv['type'] == 'put']
            iv_call = iv[iv['type'] == 'call']

            otm_put = iv_put[iv_put['inTheMoney'] == False]
            otm_call = iv_call[iv_call['inTheMoney'] == False]

            plt.plot(otm_call[['strike', j]].set_index('strike'), label = str(i) + ' call ' + '(' + str(int(otm_put.loc[otm_put['human'] == i, 'dte'].values[0])) + ' DTE)', color=plt.cm.Oranges(k), lw=3)
            plt.plot(otm_put[['strike', j]].set_index('strike'), label = str(i) + ' put ' + '(' + str(int(otm_call.loc[otm_call['human'] == i, 'dte'].values[0])) + ' DTE)', color=plt.cm.Blues(k), lw=3)

        # Dynamically size plots here

        #plt.ylim(0, 1.75)
        #plt.xlim(200, 350)

        ### Add plot title here! ###

        plt.title(symbol + ' ' + j)
        plt.legend()
        #plt.show()

        filename = path + timestamp + '_' + symbol + '_' + j + '.png'
        filenamelist.append(filename)

        plt.savefig(filename)
        plt.gcf().clear()
        plt.close()

# Symbol loop

def chart_maker(symbol):

    global newurl
    newurl = url + symbol

    df = pd.read_json(newurl)

    exp = json_normalize(data = df['optionChain']['result'], record_path = 'expirationDates')

    date_lister(symbol, exp)
    scraper(symbol)
    graph(symbol)

def actual_chart_maker_loop(symbol_list):

    global filenamelist
    filenamelist = []

    for symbol in symbol_list:
        chart_maker(symbol)

actual_chart_maker_loop(symbol_list)

### Send the charts

print('Sending...')

fromaddr = 'pythonoptionsalerts@gmail.com'
toaddr = 'samchakerian@gmail'
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = datetime.datetime.now().strftime('%Y-%m-%d') + ' Options Charts' # Put day and options alert type here

body = 'Print sick as fuck stats here.'

msg.attach(MIMEText(body, 'plain'))

for j in filenamelist:

    attachment = open(j, 'rb')

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)

    part.add_header('Content-Disposition', 'attachment; filename= %s' % j)

    msg.attach(part)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, 'yourpassword')

text = msg.as_string()
server.sendmail('youremail@gmail.com', 'youremail@gmail.com', text)
server.quit()

print('...done!')

### Make temp folder, delete .png's after. ###
shutil.rmtree(path)
