import time
import pandas as pd
from argparse import ArgumentParser
import argparse

from selenium import webdriver as wd
from selenium.webdriver import ActionChains
import selenium
import numpy as np
from schema import SCHEMA
import json
import urllib
import datetime as dt
from wordcloud import WordCloud 
import matplotlib.pyplot as plt
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
from collections import Counter


import random
import string
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


DEFAULT_URL = ('https://www.glassdoor.com/Overview/Working-at-'
               'Premise-Data-Corporation-EI_IE952471.11,35.htm')

def scrapeglassdoor(username1,password1,urlf):
    
   
    parser = ArgumentParser()
    parser.add_argument('-u', '--url',
                        help='URL of the company\'s Glassdoor landing page.',
                        default=DEFAULT_URL)
    parser.add_argument('-f', '--file', default='glassdoor_ratings.csv',
                        help='Output file.')
    parser.add_argument('--headless', action='store_true',
                        help='Run Chrome in headless mode.')
    parser.add_argument('--username', help='Email address used to sign in to GD.')
    parser.add_argument('-p', '--password', help='Password to sign in to GD.')
    parser.add_argument('-c', '--credentials', help='Credentials file')
    parser.add_argument('-l', '--limit', default=100,
                        action='store', type=int, help='Max reviews to scrape')
    parser.add_argument('--start_from_url', action='store_true',
                        help='Start scraping from the passed URL.')
    parser.add_argument(
        '--max_date', help='Latest review date to scrape.\
        Only use this option with --start_from_url.\
        You also must have sorted Glassdoor reviews ASCENDING by date.',
        type=lambda s: dt.datetime.strptime(s, "%Y-%m-%d"))
    parser.add_argument(
        '--min_date', help='Earliest review date to scrape.\
        Only use this option with --start_from_url.\
        You also must have sorted Glassdoor reviews DESCENDING by date.',
        type=lambda s: dt.datetime.strptime(s, "%Y-%m-%d"))
    args = parser.parse_args()

    if not args.start_from_url and (args.max_date or args.min_date):
        raise Exception(
            'Invalid argument combination:\
            No starting url passed, but max/min date specified.'
        )
    elif args.max_date and args.min_date:
        raise Exception(
            'Invalid argument combination:\
            Both min_date and max_date specified.'
        )

    if args.credentials:
        with open(args.credentials) as f:
            d = json.loads(f.read())
            args.username = d['username']
            args.password = d['password']
    else:
        try:
            with open('secret.json') as f:
                d = json.loads(f.read())
                args.username = d['username']
                args.password = d['password']
        except FileNotFoundError:
            msg = 'Please provide Glassdoor credentials.\
            Credentials can be provided as a secret.json file in the working\
            directory, or passed at the command line using the --username and\
            --password flags.'
            # raise Exception(msg)
            pass





    def scrape(field, review, author):

        def scrape_date(review):
            try:
                    
                date = review.find_element_by_tag_name(
                    'time').get_attribute('datetime')
                time_index = date.find(':') - 3
                res = date[:time_index]
                return res
            except:
                return False

        def scrape_emp_title(review):
            if 'Anonymous Employee' not in review.text:
                try:
                    res = author.find_element_by_class_name(
                        'authorJobTitle').text.split('-')[1]
                except Exception:
                    res = "N/A"
            else:
                res = "Anonymous"
            return res

        def scrape_location(review):
            if 'in' in review.text:
                try:
                    res = author.find_element_by_class_name(
                        'authorLocation').text
                except Exception:
                    res = np.nan
            else:
                res = "N/A"
            return res

        def scrape_status(review):
            try:
                res = author.text.split('-')[0]
            except Exception:
                res = "N/A"
            return res

        def scrape_rev_title(review):
            try:
                return review.find_element_by_class_name('summary').text.strip('"')
            except:
                return False

        def scrape_helpful(review):
            try:
                helpful = review.find_element_by_class_name('helpfulCount')
                res = helpful.text[helpful.text.find('(') + 1: -1]
            except Exception:
                res = 0
            return res

        def expand_show_more(section):
            try:
                more_link = section.find_element_by_class_name('v2__EIReviewDetailsV2__continueReading')
                more_link.click()
            except Exception:
                pass

        def scrape_pros(review):
            try:
                pros = review.find_element_by_class_name('gdReview')
                expand_show_more(pros)
                pro_index = pros.text.find('Pros')
                con_index = pros.text.find('Cons')
                res = pros.text[pro_index+5 : con_index]
            except Exception:
                res = np.nan
            return res

        def scrape_cons(review):
            try:
                cons = review.find_element_by_class_name('gdReview')
                expand_show_more(cons)
                con_index = cons.text.find('Cons')
                continue_index = cons.text.find('Continue reading')
                res = cons.text[con_index+5 : continue_index]
            except Exception:
                res = np.nan
            return res

        def scrape_advice(review):
            try:
                advice = review.find_element_by_class_name('gdReview')
                expand_show_more(advice)
                advice_index = advice.text.find('Advice to Management')
                if advice_index != -1:
                    helpful_index = advice.text.rfind('Helpful (')
                    res = advice.text[advice_index+21 : helpful_index]
                else:
                    res = np.nan
            except Exception:
                res = np.nan
            return res

        def scrape_overall_rating(review):
            try:
                ratings = review.find_element_by_class_name('gdStars')
                res = float(ratings.text[:3])
            except Exception:
                res = np.nan
            return res

        def _scrape_subrating(i):
            try:
                ratings = review.find_element_by_class_name('gdStars')
                subratings = ratings.find_element_by_class_name(
                    'subRatings').find_element_by_tag_name('ul')
                this_one = subratings.find_elements_by_tag_name('li')[i]
                res = this_one.find_element_by_class_name(
                    'gdBars').get_attribute('title')
            except Exception:
                res = np.nan
            return res

        def scrape_work_life_balance(review):
            return _scrape_subrating(0)

        def scrape_culture_and_values(review):
            return _scrape_subrating(1)

        def scrape_career_opportunities(review):
            return _scrape_subrating(2)

        def scrape_comp_and_benefits(review):
            return _scrape_subrating(3)

        def scrape_senior_management(review):
            return _scrape_subrating(4)


        def scrape_recommends(review):
            try:
                res = review.find_element_by_class_name('recommends').text
                res = res.split('\n')
                return res[0]
            except:
                return np.nan
        
        def scrape_outlook(review):
            try:
                res = review.find_element_by_class_name('recommends').text
                res = res.split('\n')
                if len(res) == 2 or len(res) == 3:
                    if 'CEO' in res[1]:
                        return np.nan
                    return res[1]
                return np.nan
            except:
                return np.nan
        
        def scrape_approve_ceo(review):
            try:
                res = review.find_element_by_class_name('recommends').text
                res = res.split('\n')
                if len(res) == 3:
                    return res[2]
                if len(res) == 2:
                    if 'CEO' in res[1]:
                        return res[1]
                return np.nan
            except:
                return np.nan


        funcs = [
            scrape_date,
            scrape_emp_title,
            scrape_location,
            scrape_status,
            scrape_rev_title,
            scrape_helpful,
            scrape_pros,
            scrape_cons,
            scrape_advice,
            scrape_overall_rating,
            scrape_work_life_balance,
            scrape_culture_and_values,
            scrape_career_opportunities,
            scrape_comp_and_benefits,
            scrape_senior_management,
            scrape_recommends,
            scrape_outlook,
            scrape_approve_ceo

        ]

        fdict = dict((s, f) for (s, f) in zip(SCHEMA, funcs))

        return fdict[field](review)


    def extract_from_page():

        def is_featured(review):
            try:
                review.find_element_by_class_name('featuredFlag')
                return True
            except selenium.common.exceptions.NoSuchElementException:
                return False

        def extract_review(review):
            try:
                author = review.find_element_by_class_name('authorInfo')
            except:
                return None # Account for reviews that have been blocked
            res = {}
            # import pdb;pdb.set_trace()
            for field in SCHEMA:
                res[field] = scrape(field, review, author)

            assert set(res.keys()) == set(SCHEMA)
            return res


        res = pd.DataFrame([], columns=SCHEMA)

        reviews = browser.find_elements_by_class_name('empReview')
        
        # refresh page if failed to load properly, else terminate the search
        if len(reviews) < 1:
            browser.refresh()
            time.sleep(5)
            reviews = browser.find_elements_by_class_name('empReview')
            if len(reviews) < 1:
                valid_page[0] = False # make sure page is populated

        for review in reviews:
            if not is_featured(review):
                data = extract_review(review)
                if data != None:
        
                    res.loc[idx[0]] = data
                else:
                    pass
            else:
                pass
            idx[0] = idx[0] + 1

        if args.max_date and \
            (pd.to_datetime(res['date']).max() > args.max_date) or \
                args.min_date and \
                (pd.to_datetime(res['date']).min() < args.min_date):
            date_limit_reached[0] = True

        return res


    def more_pages():
        try:
            current = browser.find_element_by_class_name('selected')
            pages = browser.find_element_by_class_name('pageContainer').text.split()
            if int(pages[-1]) != int(current.text):
                return True
            else:
                return False
        except selenium.common.exceptions.NoSuchElementException:
            return False


    def go_to_next_page():
        next_ = browser.find_element_by_class_name('nextButton')
        ActionChains(browser).click(next_).perform()
        time.sleep(5) # wait for ads to load
        page[0] = page[0] + 1


    def no_reviews():
        return False
        # TODO: Find a company with no reviews to test on


    def navigate_to_reviews():

        browser.get(urlf)
        time.sleep(1)

        if no_reviews():
            return False

        reviews_cell = browser.find_element_by_xpath(
            '//a[@data-label="Reviews"]')
        reviews_path = reviews_cell.get_attribute('href')
        
        # reviews_path = driver.current_url.replace('Overview','Reviews')
        browser.get(reviews_path)
        time.sleep(1)
        return True


    def sign_in():


        url = 'https://www.glassdoor.com/profile/login_input.htm'
        browser.get(url)

        # import pdb;pdb.set_trace()

        email_field = browser.find_element_by_name('username')
        password_field = browser.find_element_by_name('password')
        submit_btn = browser.find_element_by_xpath('//button[@type="submit"]')

        email_field.send_keys(username1)
        password_field.send_keys(password1)
        submit_btn.click()

        time.sleep(3)
        browser.get(urlf)



    def get_browser():
        driver = wd.Chrome("chromedriver.exe")
    
        driver.maximize_window()
        return driver


    def get_current_page():
        current = browser.find_element_by_class_name('selected')
        return int(current.text)


    def verify_date_sorting():
        ascending = urllib.parse.parse_qs(
            urlf)['sort.ascending'] == ['true']

        if args.min_date and ascending:
            raise Exception(
                'min_date required reviews to be sorted DESCENDING by date.')
        elif args.max_date and not ascending:
            raise Exception(
                'max_date requires reviews to be sorted ASCENDING by date.')


    browser = get_browser()
    page = [1]
    idx = [0]
    date_limit_reached = [False]
    valid_page = [True]


    def main():


        res = pd.DataFrame([], columns=SCHEMA)

        sign_in()

        if not args.start_from_url:
            reviews_exist = navigate_to_reviews()
            if not reviews_exist:
                return
        elif args.max_date or args.min_date:
            verify_date_sorting()
            browser.get(urlf)
            page[0] = get_current_page()
            time.sleep(1)
        else:
            browser.get(urlf)
            page[0] = get_current_page()

            time.sleep(1)

        reviews_df = extract_from_page()
        res = res.append(reviews_df)

        # import pdb;pdb.set_trace()

        while more_pages() and\
                len(res) < args.limit and\
                not date_limit_reached[0] and\
                    valid_page[0]:
            go_to_next_page()
            try:
                reviews_df = extract_from_page()
                res = res.append(reviews_df)
            except:
                break

        

        end = time.time()
        
        return res
        


    # if __name__ == '__main__':
    df = main()
    browser.close()

    dff=df
    dff["textt"] = dff['pros'].str.replace('[^\w\s]','')
    dff["textt"].replace({ r'\A\s+|\s+\Z': '', '\n' : ' '}, regex=True, inplace=True)

    dff["textt"] = dff.textt.str.lower()
    dff = dff[pd.notnull(dff['pros'])]

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

    #Calculating Negative, Positive, Neutral and Compound valuestw_list[[‘polarity’, ‘subjectivity’]] = tw_list[‘text’].apply(lambda Text: pd.Series(TextBlob(Text).sentiment))
    dff["comenttext"] = dff['cons'].str.replace('[^\w\s]','')
    dff["comenttext"].replace({ r'\A\s+|\s+\Z': '', '\n' : ' '}, regex=True, inplace=True)

    dff["comenttext"] = dff.cons.str.lower()

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
    # print ("Final Score=" +str(finalscore))



    
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

    # print('Positive Words  :',pos_word_list)    
    # print('\n\n###########################\n\n')    

    # print('Negative Words  :',neg_word_list)    

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
    










