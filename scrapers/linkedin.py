import re
import csv
from getpass import getpass
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import pandas as pd
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from textblob import TextBlob
import sys
import numpy as np

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
from getotp import get_otp
from wordcloud import WordCloud 
import matplotlib.pyplot as plt
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import Counter
import os
import random
import string
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def linkdinscrape (user,passw,company):
    driver = webdriver.Chrome("chromedriver.exe")
    
    driver.maximize_window()
    driver.get("https://www.linkedin.com/login")
    sleep(2)
    username = driver.find_element_by_xpath('//input[@name="session_key"]')
    username.send_keys(user)
    sleep(2)
    password = driver.find_element_by_xpath('//input[@name="session_password"]')
    password.send_keys(passw)
    sleep(2)
    password.send_keys(Keys.RETURN)
    
    sleep(2)
    try:
        print("tryyyyy")
        
        pin = driver.find_element_by_xpath('//input[@name="pin"]')
        sleep(30)
        print('getting pin')
        f = get_otp(user,passw)
        print('pin is')
        print(f)


        pin.send_keys(f)
        print('\n\nhello ')
        pin.send_keys(Keys.RETURN)
    except:
        pass
    sleep(3)


    driver.get("https://www.linkedin.com/company/"+company+"/posts/?feedView=all")
    sleep(2)
    def scroll2():
        scrolling = True
        last_position = driver.execute_script("return window.pageYOffset;")
    
    '''
    last_position = driver.execute_script("return window.pageYOffset;")
    scrolling = True
    print("Scrolling and loading post in DOM......\n\n")
    while scrolling:
        
                
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
    print("End of Scrolling....")
    '''
    try:
        AllPosts = driver.find_elements_by_class_name("occludable-update ")

    except NoSuchElementException:
        AllPosts=[]
        print('No posts avilabe')
        
    
    timelist=[]
    bodylistlist=[]
    likelist=[]
    comntcntlist=[]
    CommntDetailslist=[]
    comment=''
    for post in AllPosts:
        actions = ActionChains(driver)
        actions.move_to_element(post).perform()

        try:
            time=post.find_elements_by_class_name("feed-shared-actor__sub-description")
            time=time[0].text
            time = time.split(" ")
            time=time[0]
        except:
            time=""
        try:
            body=post.find_elements_by_class_name("break-words")
            body=body[0].text
            body=body.strip()
            
        except:
            body=''
        try:
            likes=post.find_elements_by_class_name("social-details-social-counts__reactions-count")

            
            likes=likes[0].text
        except:
            likes=''
            
        try:
            commentCount=post.find_elements_by_class_name("v-align-middle")


            commentCount=commentCount[1].text
        except:
            commentCount=""
        

        try:
            button = post.find_element_by_class_name("artdeco-button.artdeco-button--muted.artdeco-button--4.artdeco-button--tertiary.ember-view.comment-button.flex-wrap ")
            button.click()
            sleep(2)
            while True:
                try:

                    loadmore = post.find_element_by_class_name("comments-comments-list__load-more-comments-button.artdeco-button.artdeco-button--muted.artdeco-button--1.artdeco-button--tertiary.ember-view")
                    loadmore.click()
                    scroll2()
                    sleep(3)
                except:
                    break
            comment=""

            coments = post.find_elements_by_class_name("comments-comment-item.comments-comments-list__comment-item")

            for coment in coments:


                textt = coment.find_element_by_class_name("feed-shared-inline-show-more-text.comments-comment-item__inline-show-more-text")
                comment = comment +"+++"+ textt.text


        except:
            comment=''
            
    
                
        timelist.append(time)
        bodylistlist.append(body)
        likelist.append(likes)
        comntcntlist.append(commentCount)
        CommntDetailslist.append(comment)
        comment=''
        
        



        

    print("End of scrapping posts.....")      
    driver.close()
    print("creating DataFrame for scrapped info")
    Pt=[timelist,bodylistlist,likelist,comntcntlist,CommntDetailslist]
    df = pd.DataFrame (Pt).transpose()
    df.columns = ['Time','PostDetails','likeCount','CommentCount','CommentDetails']
    
    
    dff = df[pd.notnull(df['PostDetails'])]

    dff.drop(dff[dff['PostDetails'] ==""].index, inplace = True)

    dff["textt"] = dff['PostDetails'].str.replace('[^\w\s]','')
    dff["textt"].replace({ r'\A\s+|\s+\Z': '', '\n' : ' '}, regex=True, inplace=True)

    dff["textt"] = dff.textt.str.lower()
    dff = dff[pd.notnull(dff['PostDetails'])]



    #Calculating Negative, Positive, Neutral and Compound valuestw_list[[‘polarity’, ‘subjectivity’]] = tw_list[‘text’].apply(lambda Text: pd.Series(TextBlob(Text).sentiment))
    for index, row in dff["textt"].iteritems():
        try:
            
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
        except:
            pass
    def count_values_in_column(data,feature):
        total=data.loc[:,feature].value_counts(dropna=False)
        percentage=round(data.loc[:,feature].value_counts(dropna=False,normalize=True)*100,2)
        return pd.concat([total,percentage],axis=1,keys=['Total','Percentage'])#Count_values for sentiment
    dftext = count_values_in_column(dff,'sentiment')

    dff["comenttext"] = dff['CommentDetails'].str.replace('[^\w\s]','')
    dff["comenttext"].replace({ r'\A\s+|\s+\Z': '', '\n' : ' '}, regex=True, inplace=True)

    dff["comenttext"] = dff.comenttext.str.lower()

    #Calculating Negative, Positive, Neutral and Compound valuestw_list[[‘polarity’, ‘subjectivity’]] = tw_list[‘text’].apply(lambda Text: pd.Series(TextBlob(Text).sentiment))
    for index, row in dff["comenttext"].iteritems():
        try:
            
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
        except:
            pass

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
    


    text =  dff.textt.str.cat(sep=' ')
    text = text+ dff.comenttext.str.cat(sep=' ')
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

    
            
    return df,totallist,indexlist,finalscore ,positivewords,negativewords,negative_image,positive_image                














