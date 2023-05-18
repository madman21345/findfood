from flask import Flask, request, render_template, redirect, url_for, session, jsonify

import os
import json
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import ARRAY

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
MAPS_API_KEY = os.getenv("MAPS_API_KEY2")

# Configure database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "db.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init db
db = SQLAlchemy(app)

class Restaurant(db.Model):
  __tablename__ = "restaurants"
  
  user_id = db.Column(db.String(50), primary_key=True)  # Firebase user ID
  name = db.Column(db.String(50))
  city = db.Column(db.String(20))
  street_address = db.Column(db.String(50))
  phone_number = db.Column(db.String(20))
  bio = db.Column(db.String(200))
  
  def __init__(self, user_id, name, city, street_address, phone_number, bio, photos=[]):
    self.user_id = user_id
    self.name = name
    self.city = city
    self.street_address = street_address
    self.phone_number = phone_number
    self.bio = bio
  
  def to_dict(self):
    return {
      "user_id": self.user_id,
      "name": self.name,
      "city": self.city,
      "street_address": self.street_address,
      "phone_number": self.phone_number,
      "bio": self.bio,
    }

@app.route("/") 
def index():
  #print("ip: ",request.remote_addr)
  no_loc_available = True
  try:
    lat, lng = session["lat"], session["lng"]
    no_loc_available = False
  except:
    lat, lng = 9.5127, 122.8797
  
  print(lat, lng)
  
  #url = "https://maps.googleapis.com/maps/api/place/nearbysearch/"
  url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + str(lat) + "%2C" + str(lng) + "&radius=1500&type=restaurant&key=" + MAPS_API_KEY
  #payload = {'location': str(lat) + ',' + str(lng) , 'radius': '1500', type : 'restaurant', 'keyword' : 'mexican', 'key' : MAPS_API_KEY }

  #r = requests.get('https://httpbin.org/get', params=payload)
  payload= {}
  headers = {}

  response = requests.request("GET", url, headers=headers, data=payload)

  #print(response)
  return render_template("index.html", nlc=no_loc_available, data=response.json()['results'] )

@app.route("/findfood")
def findfood():
  no_loc_available = True
  try:
    lat, lng = session["lat"], session["lng"]
    no_loc_available = False
  except:
    lat, lng = 9.5127, 122.8797
    
  #print(lat, lng)
  
  url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + str(lat) + "%2C" + str(lng) + "&radius=25000&type=restaurant&fields=name%2Crating&key=" + MAPS_API_KEY
  
  payload={}
  headers = {}

  #data_now = json.loads(requests.request("GET", url, headers=headers, data=payload).content)
  response = requests.request("GET", url, headers=headers, data=payload)
  #stuff = response.json() #is dictionary
  #list = response['results'] 
  list = []
  for place in response.json()['results']:
    temp_dic = {}
    temp_dic['name'] = place['name']
    list.append(temp_dic)
  #morestuff = json.loads(stuffstringify())
  #data = json.loads(response)
  user = {'firstname': "Mr.", 'lastname': "My Father's Son"}
#  print(list)
  print(jsonify(response.json()))
  #return render_template("findfood.html", data=response.json())
  #return render_template("findfood.html", data=data_now)
  return response.json()


@app.route("/save_location", methods=["POST"])
def save_location():
  data = request.get_json()
  session["lat"] = data["lat"]
  session["lng"] = data["lng"]
  print("Saved!")
  return redirect(url_for("index"))

@app.route("/api/restaurants", methods=["GET"])
def get_info():
  all_restaurants = [i.to_dict() for i in Restaurant.query.all()]
  return { "payload": all_restaurants }
  
@app.route("/api/restaurants", methods=["POST"])
def add_info():
  req = request.json
  
  # Check request body for required params
  try:
    user_id = req["user_id"]
    name = req["name"]
    city = req["city"]
    street_address = req["street_address"]
    phone_number = req["phone_number"]
    bio = req["bio"]
  
  except KeyError:
    return "Missing parameter", 400
  
  try:
      new_restaurant = Restaurant(user_id, name, city, street_address, phone_number, bio)
      db.session.add(new_restaurant)
      db.session.commit()

      return new_restaurant.to_dict(), 201

  except ValueError:
    return "Server error", 500

if __name__ == "__main__":
  db.create_all()
  app.run(debug=True)

