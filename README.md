# Application of GANs to financial Time Series data

<br>Generative Adversarial Networks (GANs) have shown some outstanding results in the field of synthetic image generation. Following its success with image data the GAN architecture has also been applied to the time series problems, such as generating music, medical and financial data. 
<br>
<br>In this project I apply TimeGAN model to the stock price data and compare its performance to the regular Long Short Term Memory based network architecture. The project utilises data containing thousands of companies arranged in a panel data format and makes a multi-step stock price prediction for each company. Financial statements informatio for all companies and macroeconomic data have been obtained from open sources.


## Data
<br>Financial statements data was obtained from the U.S. Securities and Exchange Commission (SEC) website: https://www.sec.gov/dera/data/financial-statement-data-sets.html. The website contains a series of quarterly submissions starting from Q2 2009 to Q3 2020 (last date available at the point of data gathering). Collected data has been transformed into a panel format (one observation per company and date) excluding companies from the financial sector due to differences in accounting system. 
<br>Stock prices (variable name ‘Close’) have been sourced from Yahoo Finance (Python llibrary yfinance).

## Methodology
<br>The models makes four steps forward forecast (four quarters).
<br>The number of historic time steps has been restricted to the maximum of 8 quarters due to the data limitations, as some companies only have <br>five years of observations available. Using more historical information resulted in better accuracy, therefore eight time steps were selected.
<br>Adam optimizer is used for gradient update.
<br>Loss functions - combination of Binary Cross Entropy, Mean absolute and squared erros.
<br>Three types of activation functions are used: linear, sigmoid and tanh.
<br>To deal with overfitting I used early stopping, dropout layers and L2 regularisation.

### LSTM
<br>The key feature of LSTM is the addition of gates that control flow of information. Gates are composed of sigmoid activation functions and pointwise multiplication operator. Sigmoid function controls how much information to let through using data from the input layer and output state of the previous cell. 
<br>Since the input and output sequences have different length, there are two ways of how to approach it: with vector output or using encoder-decoder format. The figure below (left) illustrates vector output when the last hidden state of the LSTM layer is passed to the Dense layer, which outputs a vector of required size directly. When autoencoder is used, encoder outputs the last state of the LSTM layer which represents the encoded states of the input data. This vector is repeated to match required output dimensions and fed into decoder, Figure 11 right. Decoder then recovers the encoded states and outputs sequence into the time distributed dense layer, which produces the final set of outputs.
<br><img src="utils/LSTM_vector.png"> <img src="utils/LSTM_autoencoder.png"> 

### GANs
<br>GAN is a framework developed in 2014 to generate realistic synthetic data. While initially it was designed for image generation the model has evolved to be applied to other areas including time series. The key feature of GANs is in having two models, generator and discriminator, competing in a zero-sum game. There are multiple versions of GAN adaptation to time series tasks, I'm using TimeGAN variation (%%html
<a href="https://papers.nips.cc/paper/2019/hash/c9efe5f26cd17ba6216bbe2a7d26d490-Abstract.html">Jinsung Yoon, 2019t</a>) of GAN architecture for this project.
<br>


