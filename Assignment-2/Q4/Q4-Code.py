import pandas as pd
import numpy as np
import os
import glob



def calRSI(data, window=14):
    # simple rsi calculation
    
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))




def backTestStrat(filePath):
    # testing the strategy
    
    df = pd.read_csv(filePath, skiprows=[1])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Bollinger Bands + RSI {mean-reversion with Bollinger Bands}
    
    # start defining strategy
    
    # indicater 1, 2 & 3: Bollinger Bands (SMA20 + Upper/Lower Std Dev)
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['STD20'] = df['Close'].rolling(window=20).std()
    df['UpperBand'] = df['SMA20'] + (df['STD20'] * 2)
    df['LowerBand'] = df['SMA20'] - (df['STD20'] * 2)
    
    # indicater 4: RSI
    df['RSI'] = calRSI(df['Close'], window=14)
    
    # indicater 5: Volume SMA
    df['VolAvg'] = df['Volume'].rolling(window=20).mean()
    df['Signal'] = 0 
    

    # Buy: Price closes below the Lower Bollinger Band AND RSI says it's oversold (< 40)
    buyCond = (df['Close'] < df['LowerBand']) & (df['RSI'] < 40)
    df.loc[buyCond, 'Signal'] = 1
    
    
    # Sell: Price closes above the Upper Bollinger Band OR RSI says overbought (> 70)
    sellCond = (df['Close'] > df['UpperBand']) | (df['RSI'] > 70)
    df.loc[sellCond, 'Signal'] = -1
    
    
    # Simulate Trades
    trades = []
    poss = 0
    entryCost = 0
    entryDate = None
    
    for i, row in df.iterrows():
        
        # state machine
        if poss == 0 and row['Signal'] == 1:
            poss = 1
            entryCost = row['Close']
            entryDate = row['Date']
            
        elif poss == 1 and row['Signal'] == -1:
            poss = 0
            exitCost = row['Close']
            exitDate = row['Date']
            pctReturn = (exitCost - entryCost) / entryCost
            trades.append({
                'Entry Date': entryDate,
                'Entry Price': entryCost,
                'Exit Date': exitDate,
                'Exit Price': exitCost,
                'Return (%)': pctReturn * 100
            })
            
    tradesDF = pd.DataFrame(trades)
    
    # Calculate Metrics
    if len(tradesDF) > 0:
        totTrades = len(tradesDF)
        totReturns = tradesDF['Return (%)'].sum()
        winRate = (tradesDF['Return (%)'] > 0).mean() * 100
        
        cummReturns = (1 + tradesDF['Return (%)'] / 100).cumprod()
        peak = cummReturns.cummax()
        drawDown = (cummReturns - peak) / peak
        maxDrawDown = drawDown.min() * 100 if len(drawDown) > 0 else 0
        
        sharpe = (tradesDF['Return (%)'].mean() / tradesDF['Return (%)'].std()) if tradesDF['Return (%)'].std() != 0 else 0
        
    else:
        totTrades = 0
        totReturns = 0
        winRate = 0
        maxDrawDown = 0
        sharpe = 0
        
    mets = {
        'Total # of Trades': totTrades,
        'Total Return (%)': totReturns,
        'Sharpe Ratio': sharpe,
        'Maximum Drawdown (%)': maxDrawDown,
        'Win Rate (%)': winRate
    }
    
    return tradesDF, mets



def workFolder(folPath, splitName):
    print(f"\n ============== Working {splitName} Data ================ ")
    files = glob.glob(os.path.join(folPath, '*.csv'))
    
    for file in files:
        stockName = os.path.basename(file).split('.')[0]
        tradesDF, mets = backTestStrat(file)
        
        print(f"\nStock: {stockName}")
        for k, v in mets.items():
            print(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}")
            
        if len(tradesDF) > 0:
            ansTrainFile = f"{stockName}.csv"
            tradesDF.to_csv(ansTrainFile, index=False)
            print(f"Saved trades to {ansTrainFile}")



if __name__ == "__main__":
    baseDir = "Data-Split"
    trainDir = os.path.join(baseDir, "Train")
    testDir = os.path.join(baseDir, "Test")
    
    if os.path.exists(trainDir):
        workFolder(trainDir, "Train (10 Years)")
        
    if os.path.exists(testDir):
        workFolder(testDir, "Test (5 Years)")


"""
Authors:
    Logic and Stuct: b23406
    Formatting and improves: LLMs [deepseek, claude]
"""
