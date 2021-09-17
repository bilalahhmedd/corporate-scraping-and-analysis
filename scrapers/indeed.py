from bs4 import BeautifulSoup
import pandas as pd
import requests
from getpass import getpass
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud 
import matplotlib.pyplot as plt
import nltk
import os
from collections import Counter

import string
from time import sleep

import random
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def indeedscrapper(companyName):
    # try:
        
    df = pd.DataFrame({'review_title': [],'review':[],'author':[],'rating':[]})



    # number of pages of reviews section
    pages = 5

    end = (pages*10)+20

    # decalre this variable with company name shown in url
    #company = 'Instacart-Shoppers'
    company=str(companyName)
    temp = []




    for i in range(0,end,20):
        url = (f'https://www.indeed.com/cmp/{company}/reviews?&start={i}')
        header = {"User-Agent":"Mozilla/5.0 Gecko/20100101 Firefox/33.0 GoogleChrome/10.0"}
        page = requests.get(url,headers = header)
        soup = BeautifulSoup(page.content, 'lxml')
        results = soup.find("div", { "id" : 'cmp-container'})
        elems = results.find_all(class_='css-lqffld-Box eu4oa1w0')

        
        


        for elem in elems:
            title = elem.find(attrs = {'class':'css-1x1t5lh-Box eu4oa1w0'})

            review = elem.find('div', {'class':'css-ebcgx4-Box eu4oa1w0'})

            author = elem.find(attrs = {'class':'css-1ikgorc-Text e1wnkr790'})

            rating = elem.find(attrs = {'class':'css-1hmmasr-Text e1wnkr790'})

            idd = title.text+review.text+author.text
            if idd not in temp:
                temp.append(idd)
        
                df = df.append({'review_title': title.text,
                'review': review.text,
                'author': author.text,
                'rating': rating.text
                    }, ignore_index=True)



    dff=df
    dff["reviewtext"] = dff['review'].str.replace('[^\w\s]','')
    dff["reviewtext"].replace({ r'\A\s+|\s+\Z': '', '\n' : ' '}, regex=True, inplace=True)

    dff["reviewtext"] = dff.reviewtext.str.lower()
    for index, row in dff["reviewtext"].iteritems():
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
    dftext
    



    summ=dftext['Total'].sum()
    dftext.dropna()
    f = dftext
    f.dropna(inplace=True)
    f
    modified = f.reset_index()
    modified
    totallist = modified["Total"].tolist()
    indexlist=modified['index'].tolist()
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


    text =  dff.reviewtext.str.cat(sep=' ')
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

    positivewords=(str1.join(pos_word_list))
    negativewords=(str1.join(neg_word_list))
    name=id_generator()

    posurl='static/images/Positive'+name+'.png'
    
    
    
    positive_image="Positive"+name +".png"

    name=id_generator()

    negurl = 'static/images/Negative'+name+'.png'

    negative_image= "Negative"+ name+".png"
    
    # if os.path.exists(posurl):
    #     os.remove(posurl)
    # if os.path.exists(negurl):
    #     os.remove(negurl)
    
    # sleep(5)



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

        

    
    
    







    
                


    





    

    return df,totallist,indexlist,finalscore ,positivewords,negativewords,negative_image,positive_image
    # except:
    #     status='false'
    #     return status


        