from newspaper import Article
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import pandas as pd
import plotly.graph_objects as go

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def sentimenter(stockname):
    #this is where all the params get defined
    url = f'https://finance.yahoo.com/quote/{stockname}?p={stockname}&.tsrc=fin-srch'
    scrollmax = 20
    scrollcounter = 0

    #selenium web driver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1200x600')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    page = driver.find_element_by_tag_name('html')
    #infin scroll solution, scrolls scrollmax times
    while scrollcounter < scrollmax:  
        page.send_keys(Keys.END)
        scrollcounter+=1
        time.sleep(1)
        
    link = driver.find_elements_by_xpath('//*[@id="quoteNewsStream-0-Stream"]/ul/li[*]/div/div/div[2]/h3/a')
    linklist = []
    for item in link:
        href = item.get_attribute('href')
        linklist.append(href)    
    driver.close()

    #article parser and downloader
    full = pd.DataFrame()
    for item in linklist:
        try:
            article = Article(item)
            article.download()
            article.parse()
            title = article.title
            authors = article.authors
            body = article.text
            date = article.publish_date.strftime('%D')
            newdict = {'Title':title, 'Authors':authors, 'Date':date, 'Body':body}
            full = full.append(newdict, ignore_index=True)
        except:
            pass

    #vader analysis
    analyzer = SentimentIntensityAnalyzer()
    neg = []
    neu = []
    pos = []
    compound = []
    for item in full['Body']:
        sentiment = analyzer.polarity_scores(item)
        neg.append(sentiment['neg'])
        neu.append(sentiment['neu'])
        pos.append(sentiment['pos'])
        compound.append(sentiment['compound'])
        
    full['NegSentiment'] = neg
    full['NeuSentiment'] = neu
    full['PosSentiment'] = pos
    full['CompoundSentiment'] = compound

    #color generator (green for pos, red for neg)
    senticolor = []
    for item in full['CompoundSentiment']:
        if item > 0:
            senticolor.append('#c7d5ba')
        else:
            senticolor.append('#ff7a7a')

    #figure generator
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x= [full['Date'],full.index],
        y= full['CompoundSentiment'],
        marker_color = senticolor,
        customdata = full['Title'],
        hovertemplate = 'Title: %{customdata}; Sentiment: %{y}<extra></extra>'
    ))

    fig.update_layout(title_text=f'{stockname} News Sentiment',
                    xaxis_title='Article index and date',
                    yaxis_title='Sentiment')

    return(fig.to_html())