from scipy.special import ndtri
import numpy as np
import pandas as pd
from scipy.stats import norm
import pandas_datareader.data as web
import datetime
import math
import matplotlib.pyplot as plt


#these are the stocks we can choose in our portfolio
stocks = ['G','FB','BABA','AAPL','MSFT']

# Correlation data
tickersCorr = []  # tickers
returnsCorr = []  # for correlation matrix

# Standard deviation dictionary
stdv = dict()

#we use historical data to approximate mean and variance: MPT depends on historical data !!!
start_date = '09/18/1999'
end_date   = '09/18/2018'

#downloading the data from Yahoo! Finance
def download_data(stocks):
	data = web.DataReader(stocks,data_source='yahoo',start=start_date,end=end_date)['Adj Close']	
	return data

#if we want to calculate VaR for tomorrow
def value_at_risk(position, c, mu, sigma):
	alpha=norm.ppf(1 - c)
	var = position*(mu-sigma*alpha)
	return var
	
#we want to calculate VaR in n days time 10days
#we have to consider that the mean and standard deviation will change
#mu = mu*n and sigma=sigma*sqrt(n) we have to use these tranformations
def value_at_risk_long(S, c, mu, sigma,n):
	alpha=norm.ppf(1-c)
	var = S*(mu*n-sigma*alpha*np.sqrt(n))
	return var
	

# This function builds a correlation matrix and if plott = True plots the heat-map
def correlationMatrix(plott = False):
    cmatrix = np.corrcoef(returnsCorr)
    if plott:
        plt.imshow(cmatrix,interpolation='nearest')
        plt.colorbar()
        plt.show()
        return cmatrix
    else:
        return cmatrix 


# This function builds the variance covariance matrix given a set of tickers (stocks)
def varCovarMatrix(stocksInPortfolio):
    cm = correlationMatrix()
    vcv = []
    for eachStock in stocksInPortfolio:
        row = []
        for ticker in stocksInPortfolio:
            if eachStock == ticker:
                variance = math.pow(stdv[ticker],2)
                row.append(variance)
            else:
                cov = stdv[ticker]*stdv[eachStock]* cm[tickersCorr.index(ticker)][tickersCorr.index(eachStock)]
                row.append(cov)
        vcv.append(row)
    vcvmat = np.mat(vcv)
    return vcvmat


# This function calculates Value at Risk for the given portfolio
def VaR(stocksInPortfolio,stocksExposure,confidenceAlpha,Print = False):
    alpha = ndtri(confidenceAlpha)
    # Stocks weighs in portfolio
    weight = (np.array(stocksExposure)/sum(stocksExposure))*100
    # VarianceCovariance matrix and exposure matrix
    vcvm = varCovarMatrix(stocksInPortfolio)
    vmat = np.mat(stocksExposure)
    # Variance of portfolio in euro/usd
    varianceRR = vmat * vcvm * vmat.T
    # Value at Risk (portfolio)
    var = alpha * np.sqrt(varianceRR)
    if Print:
        print("\nPortfolio total value: ",sum(stocksExposure))
        for s, v, w in zip(stocksInPortfolio,stocksExposure,weight):
            print(s.upper(),v,"usd/euro",round(w,2),"% of portfolio")
        print("VaR: @ "+ str(confidenceAlpha*100)+"% confidence:",var,"euro/usd")
        print("VaR: "+ str(var[0][0]/sum(stocksExposure)*100)+"% of portfolio value.")
    return var

if __name__ == "__main__":
	
	S = 1e6 	#this is the investment (stocks or whatever)
	c = 0.95	#condifence level: this time it is 95%
	#stocksInPortfolio
    #stocksExposure :指的是个股票的总市值权重; 数组形式;
    
	data = download_data(stocks)
	#issue: stocksInPortfolio,stocksExposure  入参是什么类型呢？
	VaR(data,S,c,Print=True)
	
	
