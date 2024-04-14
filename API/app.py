from flask import Flask
from flask_restful import Resource, Api, reqparse
import oracledb
import datetime
import dateutil.relativedelta
import math

# Credits: https://github.com/JustTheCoolest/StockAnalyser

app = Flask(__name__)
api = Api(app)

connection = oracledb.connect(user='system', password=open('password.txt').read(), dsn='localhost:1521/xe')
cursor = connection.cursor()

def table_setup():
    # Task: Check if the existing table signature is the same as the table we are trying to create
    try:
        cursor.execute("""
        CREATE TABLE recipe(
            recipeid INT PRIMARY KEY,
            username VARCHAR(25),
            parent INT,
            location VARCHAR(255),
            vegetarianism varchar(15),
            taste VARCHAR(15),
            description TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE ingredients_lists(
            ingredient_id INT,
            quantity INT,
            recipe_id INT,
            PRIMARY KEY (ingredient_id, recipe_id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id),
            FOREIGN KEY (recipe_id) REFERENCES recipe(recipeid)
        )
        """)

        cursor.execute("""
        CREATE TABLE ingredient(
            ingredient_id INT PRIMARY KEY,
            name VARCHAR(255)
        )
        """)
    except oracledb.DatabaseError as e:
        error, = e.args
        if error.code == 955:
            #print("Table stocks already exists.")
            pass
        else:
            raise

class Recipe(Resource):
    parser = reqparse.RequestParser()  
    parser.add_argument('recipe_name', required=True)  #
    parser.add_argument('ingredients', required=True)


    def unique():
        
        # Query to retrieve details of recipes without a parent
        query = "SELECT * FROM recipe WHERE parent IS NULL"
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all the results
        recipes = cursor.fetchall()
        
        return recipes
    
    def find_parents_and_siblings(recipe_id):
        parent_and_siblings = []

        def recursive_query(recipe_id):
            cursor.execute(f"SELECT recipeid FROM recipe WHERE parent = {recipe_id}")
            results = cursor.fetchall()
            for row in results:
                parent_and_siblings.append(row[0])
                recursive_query(row[0])
        
        # Call the recursive function to find parents and siblings
        recursive_query(recipe_id)
        
        
        return parent_and_siblings



    def post(self):

        args = parser.parse_args()  # parse arguments to dictionary

        # use args['recipe_name'] and args['ingredients'] to process the posted data
        # for example, you might store it in a database or use it to update the state of your application

        return {'message': 'Recipe received', 'data': args}, 200



api.add_resource(Analyser, '/', '/<string:stock_name>')


if __name__ == "__main__":
    table_setup()
    app.run(debug=True, host='0.0.0.0')
