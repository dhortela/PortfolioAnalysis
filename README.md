# PortfolioAnalysis

### A collection of python-based financial analyses codes

  - Author: Daniel Hortelano-Roig
  - Organization: University of Oxford, UK
  - Contact: <daniel.hortelanoroig@gmail.com>

This repository is intended to contain a collection of python-based financial analyses codes. This is a work in progress.

The only code which is currently implemented is a calculation of discounted cash flows (DCFs).

## Dependencies

 The combined dependencies of all the projects in this collection are tracked here. The following packages are required as imports:

 - [argparse](https://pypi.org/project/argparse/) for input argument parsing
 - [requests](https://pypi.org/project/requests/) for sending HTTP requests
 - [bs4](https://pypi.org/project/beautifulsoup4/) for web scraping

 ## How to run a DCF calculation

To compute the DCF for a given ticker, run (using Google as an example):

 - `cd /path/to/src`
 - `python dcf.py GOOG --period_backwards 4 --discount_rate 0.08 --growth_rate 0.15 --perpetual_growth_rate 0.025`