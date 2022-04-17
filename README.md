# Application of GANs to financial Time Series data

Generative Adversarial Networks (GANs) have shown some outstanding results in the field of synthetic image generation. Following its success with image data the GAN architecture has also been applied to the time series problems, such as generating music, medical and financial data. 

In this project I apply TimeGAN model to the stock price data and compare its performance to the regular Long Short Term Memory based network architecture. The project utilises data containing thousands of companies arranged in a panel data format and makes a multi-step stock price prediction for each company. Financial statements informatio for all companies and macroeconomic data have been obtained from open sources.


## Data
Financial statements data was obtained from the U.S. Securities and Exchange Commission (SEC) website: https://www.sec.gov/dera/data/financial-statement-data-sets.html. The website contains a series of quarterly submissions starting from Q2 2009 to Q3 2020 (last date available at the point of data gathering). Collected data has been transformed into a panel format (one observation per company and date) excluding companies from the financial sector due to differences in accounting system. 
Stock prices (variable name ‘Close’) have been sourced from Yahoo Finance (Python llibrary yfinance).

## Methodology

The models make four steps forward forecast (four quarters).
The number of historic time steps has been restricted to the maximum of 8 quarters due to the data limitations, as some companies only have five years of observations available. Using more historical information resulted in better accuracy, therefore eight time steps were selected.
Adam optimizer is used for gradient update.
Loss functions - combination of Binary Cross Entropy, Mean absolute and squared erros.
Three types of activation functions are used: linear, sigmoid and tanh.
To deal with overfitting I used early stopping, dropout layers and L2 regularisation.

### LSTM
The key feature of LSTM is the addition of gates that control flow of information. Gates are composed of sigmoid activation functions and pointwise multiplication operator. Sigmoid function controls how much information to let through using data from the input layer and output state of the previous cell. 
Since the input and output sequences have different length, there are two ways of how to approach it: with vector output or using encoder-decoder format. The figure below (left) illustrates vector output when the last hidden state of the LSTM layer is passed to the Dense layer, which outputs a vector of required size directly. When autoencoder is used, encoder outputs the last state of the LSTM layer which represents the encoded states of the input data. This vector is repeated to match required output dimensions and fed into decoder, Figure 11 right. Decoder then recovers the encoded states and outputs sequence into the time distributed dense layer, which produces the final set of outputs.
<img src="utils/LSTM_autoencoder.png"> <img src="utils/LSTM_vector.png">


