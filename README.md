# finance_sentiment_analysis

### Description

This project aims to look at historical articles about the stock market and also historical stock data to model and predict monthly returns. From the articles I want to get some type of sentiment score and use that to go with other stock data to help predict next moths return

### Data Collection
For this project I will need articles, historical stock prices, and historical company financial statements
#### Articles
The articles for this project come from The NYT API and the AlphaVantage API. To begin, NYT was the only source I could think of for collecting articles, but while working on the project I came across AlphaVantage which provides much richer information for what I am trying to accomplish. THe AlphaVantage API also provides its own sentiment which I expect to be much more accurate then the sentiment I would use on the NYT articles. This is becasue I am only able to get the headline and lead paragraph, but AlphaVantage gets their sentiment from the full article.
#### Stock information
For stock price information I used AlphaVantage and also yfinance. yfinance provides the historical stock price information. AlphaVantage also provides this, but it also gives stock's historical financial statement information.

### Data Processing
The rows in the dataframe I want to create will reflect a stock at a specific month and year. The target variable will be the following month's return for the stock. Each row will have the average sentiment from various articles about that stock in that month. It will also have the financial information for the stock in that quarter.
#### Sentiment Processing
To get the sentiment is a bit tricky. There are a couple options I am considering for both articles form NYT and from AlphaVantage:
- NYT: 
For the NYT API it is more straight forward

    - Get the full text from the NYT API which combines the headline, lead paragraph, and the stock used for the query (S&P if the article is about the general market). Use BERT to provide a sentiment on this
    - Get the full text as before, but then add the previous month up to the publication date to the text (ex. some article text... <stock_name> is up/down 50%) and have BERT provide sentiment with this added information
    - Use BERT on the article text, but inject numerical information (stock return, maybe other stuff) into the second to last layer
- AlphaVantage
For AlphaVantage it is a little more complicated as there is more information that it gives per article and many ways to use all of it... so TBD
    - AlphaVantage gives the title, summary, their overall sentiment score, a list of the stocks in the article and sentiment scores specific to each one. I'm thinking the sentiments already given to the new BERT model that will give it's sentiment on the title nad summary...


- As far as averaging the sentiments from multiple articles in a month I'm thinking to weigh the sentiment from the AlphaVantage articles more because they are more financial.
### Modeling
TBH. Thinking once I have all the stock information and sentiments XGBoost to predict the next month's return

