# Application of GANs to financial Time Series data

Generative Adversarial Networks (GANs) have shown some outstanding results in the field of synthetic image generation. Following its success with image data the GAN architecture has also been applied to the time series problems, such as generating music, medical and financial data. 

In this project I apply TimeGAN model to the stock price data and compare its performance to the regular Long Short Term Memory based network architecture. The project utilises data containing thousands of companies arranged in a panel data format and makes a multi-step stock price prediction for each company. Financial statements informatio for all companies and macroeconomic data have been obtained from open sources.


## Data
Financial statements data was obtained from the U.S. Securities and Exchange Commission (SEC) website: https://www.sec.gov/dera/data/financial-statement-data-sets.html. The website contains a series of quarterly submissions starting from Q2 2009 to Q3 2020 (last date available at the point of data gathering). Collected data has been transformed into a panel format (one observation per company and date) excluding companies from the financial sector due to differences in accounting system. 
Stock prices (variable name ‘Close’) have been sourced from Yahoo Finance (Python llibrary yfinance).

