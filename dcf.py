####
# Author: Daniel Hortelano Roig
# Email: daniel.hortelanoroig@gmail.com
# Date: 08/04/2024

# Computes discounted cash flow (DCF) per shares for a given ticker (e.g.: GOOG).
# Web scrapes the following directly from Yahoo Finance:
# (1) Free cash flow (FCF)
# (2) Total cash (TC)
# (3) Total debt (TD)
# (4) Outstanding Shares (OS)
####

import argparse
import json
import requests
from bs4 import BeautifulSoup


####### Function definitions


def CalculateDCFDensity(fcf,periodForwards,growthRate,perpetualGrowthRate,discountRate,totalCash,totalDebt,outstandingShares):
    
    tlist = list(range(1,periodForwards+2))
    
    ffcf = []
    pvffcf = []
    fcf0 = fcf[-1]
    
    ffcf.append(fcf0 * (1 + growthRate))
    pvffcf.append(ffcf[0] / (1 + discountRate)**tlist[0])
    
    dcftotal = 0
    for i in range(1,periodForwards):
        ffcf.append(ffcf[i-1] * (1 + growthRate))
        pvffcf.append(ffcf[i] / (1 + discountRate)**tlist[i])
    
    ffcf.append(ffcf[-1] * (1 + perpetualGrowthRate)/(discountRate - perpetualGrowthRate))
    pvffcf.append(ffcf[-1] / (1 + discountRate)**tlist[-1])
    
    pvffcfSum = sum(pvffcf)
    
    equityValue = pvffcfSum + totalCash - totalDebt
    
    dcfdensity = equityValue / outstandingShares
    
    return dcfdensity

def GetOutstandingShares(ticker,header):
    
    url = 'https://uk.finance.yahoo.com/quote/{}/key-statistics'.format(ticker)
    page = requests.get(url, headers=header)
    
    # Check HTTP status code for unexpected errors:
    CheckHTTPStatusCode(page.status_code)
    
    # Obtain HTML tree:
    soup = BeautifulSoup(page.text,features='lxml')
    
    # Obtain OS:
    ostag = soup.find_all(\
    attrs={"aria-label": "'Shares outstanding' is taken from the most-recently filed quarterly or annual report, and 'market cap' is calculated using shares outstanding."}\
    )[0].parent.parent.find_all('td')[-1]
    ostext = ostag.text
    os = float(ostext.replace('B', '')) * 1e9
    
    return os

def GetTotalDebt(ticker,header):
    
    url = 'https://finance.yahoo.com/quote/{}/balance-sheet'.format(ticker)
    page = requests.get(url, headers=header)
    
    # Check HTTP status code for unexpected errors:
    CheckHTTPStatusCode(page.status_code)
    
    # Obtain HTML tree:
    soup = BeautifulSoup(page.text,features='lxml')
    
    # Obtain TD:
    tdtag = soup.find_all(attrs={"title": "Total Debt"})[0].parent.parent.find_all('span')[1]
    td = float(tdtag.text.replace(',', '')) * 1000
    
    return td

def GetTotalCash(ticker,header):
    
    url = 'https://uk.finance.yahoo.com/quote/{}/balance-sheet'.format(ticker)
    page = requests.get(url, headers=header)
    
    # Check HTTP status code for unexpected errors:
    CheckHTTPStatusCode(page.status_code)
    
    # Obtain HTML tree:
    soup = BeautifulSoup(page.text,features='lxml')
    
    # Obtain TC:
    tctag = soup.find_all(attrs={"title": "Total cash"})[0].parent.parent.find_all('span')[1]
    tc = float(tctag.text.replace(',', '')) * 1000
    
    return tc
    

def GetFreeCashFlow(ticker,header,t):
    # Output: list of FCFs from current year to past t years
    
    url = 'https://uk.finance.yahoo.com/quote/{}/cash-flow'.format(ticker)
    page = requests.get(url, headers=header)
    if t > 4:
        raise Exception("Too many years in past for Yahoo Finance data")
    elif t < 1:
        raise Exception("Too years in past is less than one")
    
    # Check HTTP status code for unexpected errors:
    CheckHTTPStatusCode(page.status_code)
    
    # Obtain HTML tree:
    soup = BeautifulSoup(page.text,features='lxml')
    
    # Obtain FCF:
    fcftagparent = soup.find_all(attrs={"title": "Free cash flow"})[1].parent.parent
    fcftag = fcftagparent.find_all('span')[2:t+2]
    fcf0list = [float(string.text.replace(',', '')) for string in fcftag]
    fcflist = [fcf * 1000 for fcf in fcf0list]
    
    try:
        assert t <= len(fcflist)
    except AssertionError:
        fcflist = fcflist[:t]
    except:
        fcflist = fcflist[:1] # Only most recent FCF
    
    fcflist.reverse()
    
    return fcflist

def CheckHTTPStatusCode(status_code):
    if str(status_code)[0] == '1':
        pass # Good behaviour
    elif str(status_code)[0] == '2':
        pass # Good behaviour
    elif str(status_code)[0] == '3':
        raise Exception("HTTP status: 3xx redirection")
    elif str(status_code)[0] == '4':
        raise Exception("HTTP status: 4xx client error")
    elif str(status_code)[0] == '5':
        raise Exception("HTTP status: 5xx client error")


####### Main


if __name__ == "__main__":
    
    # Define input arguments:
    argparser = argparse.ArgumentParser()
    argparser.add_argument('ticker', help='Ticker to analyse. Example: GOOG')
    argparser.add_argument('-pf','--period_forwards', help='Time period forwards in years. Default: 4', type=int, default=4)
    argparser.add_argument('-pb','--period_backwards', help='Time period backwards in years. Default: 4', type=int, default=4)
    argparser.add_argument('-dr','--discount_rate', help='Discount rate estimate. Default: 0.08 (8%)', type=float, default=0.08)
    argparser.add_argument('-gr','--growth_rate', help='Free cash flow growth rate estimate. Default: 0.15 (15%)', type=float, default=0.15)
    argparser.add_argument('-pge','--perpetual_growth_rate', help='Perpetual growth rate estimate. Default: 0.025 (2.5%)', type=float, default=0.025)
    argparser.add_argument('-header','--header', help='Header used to access HTML', type=json.loads, default={"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"})
    args = argparser.parse_args()
    
    # Extract inputs:
    ticker = args.ticker
    periodForwards = args.period_forwards
    periodBackwards = args.period_backwards
    discountRate = args.discount_rate
    growthRate = args.growth_rate
    perpetualGrowthRate = args.perpetual_growth_rate
    if args.header is None:
        header = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
    else:
        header = args.header
    
    print("\nCalculating DCF density for: ${}\n".format(ticker))
    
    # Obtain variables for DCF calculation:
    freeCashFlow = GetFreeCashFlow(ticker,header,periodBackwards)
    print("Free cash flows obtained.")
    totalCash = GetTotalCash(ticker,header)
    print("Total cash obtained.")
    totalDebt = GetTotalDebt(ticker,header)
    print("Total debt obtained.")
    outstandingShares = GetOutstandingShares(ticker,header)
    print("Outstanding shares obtained.")
    
    # Perform calculations:
    discountedCashFlow = CalculateDCFDensity(\
        freeCashFlow,periodForwards,growthRate,perpetualGrowthRate,discountRate,totalCash,totalDebt,outstandingShares)
    
    
    print("\nDCF price per share: {} USD\n".format(discountedCashFlow))
