from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

application = Flask(__name__) # initializing a flask app
app=application

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST' :
        try :
            searchstring = request.form["content"].replace(" " , "")
            games_link = "https://play.google.com/store/search?q=" + searchstring
            uClient = uReq(games_link)
            games_page = uClient.read()
            uClient.close()
            game_html = bs(games_page , 'html.parser')
            bigboxes = game_html.findAll("div" , {"class" : "ULeU3b"})
            del(bigboxes[0:3])
            box = bigboxes[0]
            games_link = "https://play.google.com" + box.a["href"]
            prodresp = requests.get(games_link)
            prod_html = bs(prodresp.text , "html.parser")
            review_boxes = prod_html.findAll("div" , {"class" : "EGFGHd"})

            filename = searchstring + ".csv"
            fw = open(filename , "w")
            headers = "Game, Name, Rating, Date, Comment \n"
            fw.write(headers)
            reviews = []
            for i in review_boxes :
                try :
                    name = i.findAll("div" , {"class" : "X5PpBb"})[0].text
                except :
                    logging.info("name")

                try :
                    date = i.findAll("span" , {"class" : "bp9Aid"})[0].text
                except :
                    logging.info("date")

                try :
                    rating = i.findAll("div" , {"class" : "iXRFPc"})[0]["aria-label"]
                
                except :
                    rating = "no rating"
                    logging.info('rating')
                
                try :
                    comment = i.findAll("div" , {"class" : "h3YV2d"})[0].text
                except :
                    comment = "no comment"

                try :
                    game = prod_html.findAll("h1" , {"class" : "Fd93Bb"})[0].text
                except :
                    game = "no game"
                my_dict = {"Game" : game , "Name" : name , "Rating" : rating , "Date" : date , "Comments" : comment}
                reviews.append(my_dict)
            client = pymongo.MongoClient("mongodb+srv://rk7018295:tonystark369@cluster0.ckt1qtj.mongodb.net/")
            db = client["website_database"]
            review_collection = db["review collection"]
            review_collection.insert_many(reviews)
            logging.info(f"log my final result {reviews}")
            return render_template("result.html" , reviews = reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'    

    else :
        render_template('index.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
	#app.run(debug=True)
