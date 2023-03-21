from flask import Flask, jsonify, render_template, request
from sqlalchemy.sql.expression import func, select
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
import random

db = SQLAlchemy()
app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)



##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    # Section 553: 2
    def to_dict(self):
    #     Method 1:
    #     dictionary = {}
    # Loop through each column in the data record
    #     for column in self.__table__.columns:
    # Create a new dictionary entry;
    # where the key is the name of the column
    # and the value is the value of the column
    #         dictionary[column.name] = getattr(self, column.name)
    #     return dictionary

    # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    #TODO: MIGHT NEED THIS LATER
    # def __repr__(self):
    #     return f'<Cafe {self.name}'


with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

## HTTP GET - Read Record
# Inludes Section 551: 1,2
@app.route('/random', methods=['GET'])
def get_random_cafe():
    all_cafe = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafe)
    print(random_cafe)

    # Turn random_cafe Object into a Json. This is called serialization: Flask has a serialization method called jsonify() Documentation: https://www.adamsmith.haus/python/docs/flask.jsonify
    #The Following is going to be the long method. Refer to def to_dict to automize and make the code more effecient:
    # return jsonify(cafe={
    #     #'id': random_cafe.id,
    #     'name': random_cafe.name,
    #     'map_url': random_cafe.map_url,
    #     'img_url': random_cafe.img_url,
    #     'location': random_cafe.location,
    #     'seats': random_cafe.seats,
    #
    #     'amenities': {
    #         'has_toilet': random_cafe.has_toilet,
    #         'has_wifi': random_cafe.has_wifi,
    #         'has_sockets': random_cafe.has_sockets,
    #         'can_take_calls': random_cafe.can_take_calls,
    #         'coffee_price': random_cafe.coffee_price}
    #
    # })

    # This is the short version to the code above. It plays from method 2 out of def to_dict to produce the return
    return jsonify(cafe=random_cafe.to_dict())
    

# HTTP GET - Read Record
# Includes Section 552: 1
@app.route('/all', methods=['GET'])
def get_all_cafe():
    # Creates a dictionary to put the db into.
    cafes = {'cafes': []}
    # Pulls all db and puts into a list
    all_cafe = db.session.query(Cafe).all()
    #For Loop converts db data into a dictionary so it can produce the jsonify
    for cafe in all_cafe:
        cafe = dict(cafe.__dict__)
        del cafe['_sa_instance_state']
        cafes['cafes'].append(cafe)
    return jsonify(cafes)

# Includes Section 553
@app.route('/search', methods=['GET'])
def search():
    # Pulls the location information from the user
    query_location = request.args.get("loc")
    # Pulls Data from the db, and filters out anything that doesnt match the code above
    cafe_by_location = db.session.query(Cafe).filter_by(location=query_location).all()
    # If there is a db match it will print below
    if cafe_by_location:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafe_by_location])
    else:
        return jsonify(error={"Not Found": "Sorry, We do not have cafe at this location"})

## HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add_cafe():
    cafe_response = request.form.to_dict()
    for key, value in cafe_response.items():
        if value.lower() == "true":
            cafe_response[key] = bool('True')
        elif value.lower() == "false":
            # if no values given to bool() it will return false
            cafe_response[key] = bool('')
            print(cafe_response[key])

    cafe = Cafe(**cafe_response)
    db.session.add(cafe)
    db.session.commit()
    success = {
        "success": "Successfully added new cafe"
    }
    return jsonify(
        response=success,
    )

# Update Price of Coffee
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        cafe.coffee_price = request.args.get("new_price")
        db.session.commit()
        return jsonify(response={"Success": "Successfully updated the price."})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found on the database."})

@app.route('/report-closed/<int:cafe_id>', methods=['GET','DELETE'])
def cafe_delete(cafe_id):
    # Gets the api-key
    api_key = request.args.get('api-key')
    # Checks if the api-key matches
    if api_key == 'TopSecretApiKey':
        #Get the db row that is associated with the cafe ID
        cafe = db.session.query(Cafe).get(cafe_id)
        #If there is a cafe id that matches in the DB
        if cafe:
            #Deletes the row
            db.session.delete(cafe)
            db.session.commit()
            #Success Response
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200  # 200 code means OK
        # IF there isnt a row in the db that matches the id
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404  # 404 code means "Not Found"
    # Does not have the correct api-key, not allowed access
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403 # 403 code means "Forbidden

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
