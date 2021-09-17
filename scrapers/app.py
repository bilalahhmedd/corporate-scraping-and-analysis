from flask import Flask, render_template, url_for, request, redirect
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from wordcloud import WordCloud 
import matplotlib.pyplot as plt
from collections import Counter
import os




from indeed import indeedscrapper

from linkedin import linkdinscrape

from twitter import twitterScrape

from glassdoor import scrapeglassdoor
import validators


class CleanCache:
	'''
	this class is responsible to clear any residual image files
	present due to the past searches made.
	'''
	def __init__(self, directory=None):
		self.clean_path = directory
		# only proceed if directory is not empty
		if os.listdir(self.clean_path) != list():
			# iterate over the files and remove each file
			files = os.listdir(self.clean_path)
			for fileName in files:
				print(fileName)
				os.remove(os.path.join(self.clean_path,fileName))
		print("cleaned!")

app = Flask(__name__)
app.config['UPLOAD_FOLDER']=os.path.join("static","images")


colors = [
    "#0071e3", "#1bb364",    "#ff0000" , "#288bb5"]




@app.route('/', methods=['POST', 'GET'])
def index():
    
    if request.method == 'POST':
        return  render_template('invalid.html')


    else:
        

        return render_template('index.html' )

@app.route('/scrape', methods=['POST', 'GET'])
def scrape():
    app.config["CACHE_TYPE"] = "null"
    CleanCache(directory=app.config['UPLOAD_FOLDER'])

    if request.method == 'POST':
        if request.form['Scraper']=='indeed':

            comp = request.form['content']
            comp =comp.replace(" ", "")
            if (comp != ""):
                try:


                    df,totallist,indexlist,finalscore,positivewords,negativewords,negurl,posurl = indeedscrapper(comp)
                    positive_image = os.path.join(app.config['UPLOAD_FOLDER'], posurl)
                    negative_image = os.path.join(app.config['UPLOAD_FOLDER'], negurl)
                    

                    return  render_template('result.html',tables=[df.to_html(classes='data table table-striped table-bordered', table_id = 'example' )], titles=df.columns.values,set=zip(totallist, indexlist, colors), finalscore = round(finalscore),positivewords=positivewords,negativewords= negativewords, posurl= positive_image,negurl=negative_image,name="Indeed")

                except:
                    return  render_template('invalid.html')
            else:
                meassage="Search Company is Required "
                # return redirect(url_for('index', message=meassage))
                return render_template('index.html', message=meassage)

        elif request.form['Scraper']=='linkedinn':

            comp = request.form['content']
            comp =comp.replace(" ", "")
            user = request.form['user']
            user = user.replace(" ","")
            password =request.form['password']
            # password = password.replace(" ","")
            if validators.email(user) and comp !="" and password != "":
                


                # try:



                    df,totallist,indexlist,finalscore,positivewords,negativewords,negurl,posurl = linkdinscrape(user,password,comp)
                    positive_image = os.path.join(app.config['UPLOAD_FOLDER'], posurl)
                    negative_image = os.path.join(app.config['UPLOAD_FOLDER'], negurl)
                    return  render_template('result.html',tables=[df.to_html(classes='data table table-striped table-bordered', table_id = 'example' )], titles=df.columns.values,set=zip(totallist, indexlist, colors), finalscore = round(finalscore),positivewords=positivewords,negativewords= negativewords, posurl= positive_image,negurl=negative_image,name="LinkedInn")

                # except:
                #     return  render_template('invalid.html')
            else:
                meassage="All Feilds are Required \n\nEmail Should be in Correct formate "
                # return redirect(url_for('index', message=meassage))
                return render_template('index.html', message=meassage)

        elif request.form['Scraper']=='twitter':

            comp = request.form['content']
            comp =comp.replace(" ", "")
            user = request.form['user']
            user = user.replace(" ","")
            password =request.form['password']
            # password = password.replace(" ","")

            if user != "" and comp !="" and password != "":


            
                # try:


                    df,totallist,indexlist,finalscore,positivewords,negativewords,negurl,posurl = twitterScrape(user,password,comp)
                    
                    positive_image = os.path.join(app.config['UPLOAD_FOLDER'], posurl)
                    negative_image = os.path.join(app.config['UPLOAD_FOLDER'], negurl)
                    
                    return  render_template('result.html',tables=[df.to_html(classes='data table table-striped table-bordered', table_id = 'example' )], titles=df.columns.values,set=zip(totallist, indexlist, colors), finalscore = round(finalscore),positivewords=positivewords,negativewords= negativewords, posurl= positive_image,negurl=negative_image,name="Twitter")

                # except:
                #     return  render_template('invalid.html')
            else:
                meassage="All Feilds are Required "
                # return redirect(url_for('index', message=meassage))
                return render_template('index.html', message=meassage)

        elif request.form['Scraper']=='glassdoor':

            comp = request.form['content']
            
            user = request.form['user']
            
            password =request.form['password']
            

            if validators.url(comp) and validators.email(user) and password != "":
                
                if (comp.startswith("https://www.glassdoor.com/Overview/")):

                    try:


                        df,totallist,indexlist,finalscore,positivewords,negativewords,negurl,posurl = scrapeglassdoor(user,password,comp)
                        
                        positive_image = os.path.join(app.config['UPLOAD_FOLDER'], posurl)
                        
                        negative_image = os.path.join(app.config['UPLOAD_FOLDER'], negurl)
                        
                        return  render_template('result.html',tables=[df.to_html(classes='data table table-striped table-bordered', table_id = 'example' )], titles=df.columns.values,set=zip(totallist, indexlist, colors), finalscore = round(finalscore),positivewords=positivewords,negativewords= negativewords, posurl= positive_image,negurl=negative_image,name="GlassDoor")

                    except:
                        return  render_template('invalid.html')
                
                else:
                    meassage="The URL shoud be the landing page Of GlassDoor "
                    # return redirect(url_for('index', message=meassage))
                    return render_template('index.html', message=meassage)
                
            else:
                meassage="*All Feilds are Required                       *Email Should be in Correct formate \n\n       * Search Should be url"
                # return redirect(url_for('index', message=meassage))
                return render_template('index.html', message=meassage)
                



        
        else:

            return render_template('invalid.html')#tables=[df.to_html(classes='data')], titles=df.columns.values)












if __name__ == "__main__":
    app.run()
