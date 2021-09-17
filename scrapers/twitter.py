from textblob import TextBlob
import sys
import numpy as np
import os
import nltk
import pycountry
import re
import string
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from langdetect import detect
from nltk.stem import SnowballStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import pandas as pd
import re
import csv
from getpass import getpass
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from collections import Counter
from wordcloud import WordCloud 
import matplotlib.pyplot as plt
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import random
import string
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def twitterScrape (user,my_password,search_term):
    driver = webdriver.Chrome("chromedriver.exe")
    driver.maximize_window()

    sleep(3)
    print('driver initiated')
    driver.get("https://www.twitter.com/login")
    sleep(3)
    print('website loaded')
    username = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]')
    username.send_keys(user)
    password = driver.find_element_by_xpath('//input[@name="session[password]"]')
    password.send_keys(my_password)
    password.send_keys(Keys.RETURN)
    #put delay
    sleep(15)


    driver.get("https://twitter.com/search?q=%23"+search_term+"&src=typed_query")
    # search_input = driver.find_element_by_xpath('//input[@placeholder="Search Twitter"]')
    # search_input.send_keys(search_term)
    # search_input.send_keys(Keys.RETURN)
    sleep(15)



    #to filter tweet for the people we follow 
    filterr = driver.find_elements_by_class_name("r-1p0dtai.r-1ei5mc7.r-1pi2tsx.r-1d2f490.r-crgep1.r-orgf3d.r-t60dpp.r-u8s1d.r-zchlnj.r-ipm5af.r-13qz1uu")
    filterr[1].click()
    sleep(3)

    def get_tweet_data(card):
        """Extract data from tweet card"""
        sleep(1)
        try:
            username = card.find_element_by_xpath('.//span').text
        except:
            username=""
        try:
            handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
        except NoSuchElementException:
            return
        
    
        try:
            comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
        except:
            comment=""
        try:
            responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
        except:
            responding=""
        
        text = comment + responding
        
        try:
            reply_cnt = card.find_element_by_xpath('.//div[@data-testid="reply"]').text
        except:
            reply_cnt=""
        try:
            retweet_cnt = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
        
        except:
            retweet_cnt=""
        try:
            like_cnt = card.find_element_by_xpath('.//div[@data-testid="like"]').text
        
        except:
            like_cnt=""
        
        try:



            commenttt = card.find_element_by_xpath('.//div[2]/div[1]/div[1]/div[1]/div[1]/a')
            link = commenttt.get_attribute("href")
        except:
            link=''
        tweet = (username, handle, text, reply_cnt, retweet_cnt, like_cnt,link)
        

        
        
        return tweet    
    

    # get all tweets on the page
    data = []
    tweet_ids = set()
    last_position = driver.execute_script("return window.pageYOffset;")
    scrolling = True

    while scrolling:
        page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
        for card in page_cards[:20]:
            tweet = get_tweet_data(card)
            if tweet:
                tweet_id = ''.join(tweet)
                if tweet_id not in tweet_ids:
                    tweet_ids.add(tweet_id)
                    data.append(tweet)
                
        scroll_attempt = 0
        while True:
            # check scroll position
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(2)
            curr_position = driver.execute_script("return window.pageYOffset;")
            if last_position == curr_position:
                scroll_attempt += 1
                
                # end of scroll region
                if scroll_attempt >= 0:
                    scrolling = False
                    break
                else:
                    sleep(2) # attempt another scroll
            else:
                last_position = curr_position
                
                break

    with open('tweetoutput.csv', 'w', newline='', encoding='utf-8') as f:
        header = ['UserName', 'Handle',  'Text', 'Comments', 'Likes', 'Retweets','link']
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data) 
    pd.set_option('display.max_columns', None)
    df = pd.read_csv('tweetoutput.csv')
    if os.path.exists("tweetoutput.csv"):
        os.remove("tweetoutput.csv")
    df["Comments"].fillna("", inplace = True)

    def get_tweet_data2(card):
        """Extract data from tweet card"""
        username = card.find_element_by_xpath('.//span').text
        try:
            handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
        except NoSuchElementException:
            return
        try:
            com = card.find_element_by_xpath('.//div[2]/div[2]/div[2]/div[1]/span').text
        except NoSuchElementException:
            return
        tweet = (username, handle, com )
        return tweet   
    
   
    for ind ,row in df.iterrows():
        if row["Comments"]!='':
            try:
                driver.get(row["link"])
                sleep(2)
                data = []
                tweet_ids = set()
                last_position = driver.execute_script("return window.pageYOffset;")
                scrolling = True

                while scrolling:
                    page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
                    for card in page_cards[:20]:
                        tweet = get_tweet_data2(card)
                        if tweet:
                            tweet_id = ''.join(tweet)
                            if tweet_id not in tweet_ids:
                                tweet_ids.add(tweet_id)
                                data.append(tweet)

                    scroll_attempt = 0
                    while True:
                        # check scroll position
                        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                        sleep(2)
                        curr_position = driver.execute_script("return window.pageYOffset;")
                        if last_position == curr_position:
                            scroll_attempt += 1

                            # end of scroll region
                            if scroll_attempt >= 2:
                                scrolling = False
                                break
                            else:
                                sleep(2) # attempt another scroll
                        else:
                            last_position = curr_position

                            break
                st=''
                for x in data:
                    st = (st+str(x[1])+" "+str(x[2]) +'  +  ' ) 
                df.loc[ind,"Tweet Details"]=st
    #             df.loc[ind,"len"]=len(data)
                


                
                
            except:
                pass
                    





        
        
                    
    print("done.......")
    driver.close()


    dff=df
    dfr=df
    dff["textt"] = dff['Text'].str.replace('[^\w\s]','')
    dff["textt"].replace({ r'\A\s+|\s+\Z': '', '\n' : ' '}, regex=True, inplace=True)

    dff["textt"] = dff.textt.str.lower()
    #Calculating Negative, Positive, Neutral and Compound valuestw_list[[‘polarity’, ‘subjectivity’]] = tw_list[‘text’].apply(lambda Text: pd.Series(TextBlob(Text).sentiment))
    for index, row in dff["textt"].iteritems():
        score = SentimentIntensityAnalyzer().polarity_scores(row)
        neg = score['neg']
        neu = score['neu']
        pos = score['pos']
        comp = score['compound']
        if neg > pos:
            dff.loc[index, 'sentiment'] = 'negative'
        elif pos > neg:
            dff.loc[index, 'sentiment'] = 'positive'
        else:
            dff.loc[index, 'sentiment'] = 'neutral'
        dff.loc[index, 'neg'] = neg
        dff.loc[index, 'neu'] = neu
        dff.loc[index, 'pos'] = pos
        dff.loc[index, 'compound'] = comp

    def count_values_in_column(data,feature):
        total=data.loc[:,feature].value_counts(dropna=False)
        percentage=round(data.loc[:,feature].value_counts(dropna=False,normalize=True)*100,2)
        return pd.concat([total,percentage],axis=1,keys=['Total','Percentage'])#Count_values for sentiment
    dftext = count_values_in_column(dff,'sentiment')
    dff["comenttext"] = dff['Tweet Details'].str.replace('[^\w\s]','')
    dff["comenttext"].replace({ r'\A\s+|\s+\Z': '', '\n' : ' '}, regex=True, inplace=True)

    dff["comenttext"] = dff.comenttext.str.lower()
    
    #Calculating Negative, Positive, Neutral and Compound valuestw_list[[‘polarity’, ‘subjectivity’]] = tw_list[‘text’].apply(lambda Text: pd.Series(TextBlob(Text).sentiment))
    for index, row in dff["textt"].iteritems():
        score = SentimentIntensityAnalyzer().polarity_scores(row)
        neg = score['neg']
        neu = score['neu']
        pos = score['pos']
        comp = score['compound']
        if neg > pos:
            dff.loc[index, 'CommentSentiment'] = 'negative'
        elif pos > neg:
            dff.loc[index, 'CommentSentiment'] = 'positive'
        else:
            dff.loc[index, 'CommentSentiment'] = 'neutral'
        dff.loc[index, 'commentneg'] = neg
        dff.loc[index, 'commentneu'] = neu
        dff.loc[index, 'commentpos'] = pos
        dff.loc[index, 'commentcompound'] = comp
    dfcomment = count_values_in_column(dff,'CommentSentiment')
    summ= dfcomment['Total'].sum() +dftext['Total'].sum()
    summ
    dfcomment.dropna()
    dftext.dropna()
    dfcomment
    f = dfcomment +dftext
    f.dropna(inplace=True)
    f
    modified = f.reset_index()
    modified
    try:
        
        ng=modified[modified['index'] =="negative"]
        ng=ng["Total"].tolist()
        ng=ng[0]
    except:
        ng=0
    try:
        
        nu=modified[modified['index'] =="neutral"]
        nu=nu["Total"].tolist()
        nu=nu[0]
    except:
        nu=0
    nu
    try:
        p=modified[modified['index'] =="positive"]
        p=p["Total"].tolist()
        p=p[0]
    except:
        p=0

    finalscore=((p+nu)/summ)*100

    text =  df.textt.str.cat(sep=' ')
    text = text+ df.comenttext.str.cat(sep=' ')
    li = list(text.split(" "))
    test_subset= li
    sid = SentimentIntensityAnalyzer()
    pos_word_list=[]
    neu_word_list=[]
    neg_word_list=[]

    for word in test_subset:
        if (sid.polarity_scores(word)['compound']) >= 0.5:
            pos_word_list.append(word)
        elif (sid.polarity_scores(word)['compound']) <= -0.5:
            neg_word_list.append(word)
        else:
            neu_word_list.append(word)                


    str1 = " , " 

    pos_word_list=list(set(pos_word_list))
    neg_word_list= list(set(neg_word_list))
        
    positivewords=(str1.join(pos_word_list))
    negativewords=(str1.join(neg_word_list))

    name=id_generator()

    posurl='static/images/Positive'+name+'.png'
    
    
    
    positive_image="Positive"+name +".png"

    name=id_generator()

    negurl = 'static/images/Negative'+name+'.png'

    negative_image= "Negative"+ name+".png"
    


    
    if not pos_word_list:
        pos_word_list1=["Empty"]
        word_could_dict=Counter(pos_word_list1)
        wordcloud = WordCloud(width = 1000, height = 500).generate_from_frequencies(word_could_dict)
        wordcloud.to_file(posurl)
    else:
        word_could_dict=Counter(pos_word_list)
        wordcloud = WordCloud(width = 1000, height = 500).generate_from_frequencies(word_could_dict)
        wordcloud.to_file(posurl)
    

    if not neg_word_list:
        neg_word_list1=["Empty"]
        word_could_dict=Counter(neg_word_list1)
        wordcloud = WordCloud(width = 1000, height = 500).generate_from_frequencies(word_could_dict)
        wordcloud.to_file(negurl) 
    else:
        word_could_dict=Counter(neg_word_list)
        wordcloud = WordCloud(width = 1000, height = 500).generate_from_frequencies(word_could_dict)
        wordcloud.to_file(negurl)
    
    totallist = modified["Total"].tolist()
    indexlist=modified['index'].tolist()

    
            
    return dfr,totallist,indexlist,finalscore ,positivewords,negativewords,negative_image,positive_image












