

"""
2. Obtain the Past 15 years of daily stock data. Use the following time split for training and testing trading strategies.

    Dataset     Period              Purpose
    Training    First 10 years      Strategy design
    Testing     Last 5 years        Out-of-sample evaluation

"""

"""
Exchange	Sector	        Stock Name	        Symbol
NSE	        Banking	        HDFC Bank	        HDFCBANK
NSE	        IT	            Infosys	            INFY
NSE	        Automobile	    Maruti Suzuki	    MARUTI
NSE	        Pharmaceutical	Sun Pharma	        SUNPHARMA
"""


# source ass2/bin/activate

import yfinance as yf
import pandas as pd

stocks = ["HDFCBANK.NS", "SUNPHARMA.NS", "MARUTI.NS", "INFY.NS"]

ticker = "SUNPHARMA.NS" 
data = yf.download(
    ticker,
    start="2010-01-01",
    end=None,
    interval="1d"
)
data.to_csv("SUNPHARMA.csv")
print("Done")

from datetime import datetime

ticker = "SUNPHARMA.NS"
data = yf.download(
    ticker,
    start="2010-01-01",
    progress=False
)

data.reset_index(inplace=True)
today = datetime.today()

testStart = today.replace(year=today.year - 5)
train = data[data["Date"] < testStart]
test  = data[data["Date"] >= testStart]

train.to_csv("TrainSUNPHARMA.csv", index=False)
test.to_csv("TestSUNPHARMA.csv", index=False)

print("Train shape:", train.shape)
print("Test shape:", test.shape)

