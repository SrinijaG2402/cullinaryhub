from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import oracledb
import datetime
import dateutil.relativedelta
import math

# Credits: https://github.com/JustTheCoolest/StockAnalyser

app = Flask(__name__)
CORS(app)
api = Api(app)

connection = oracledb.connect(user='system', password=open('password.txt').read(), dsn='localhost:1521/xe')
cursor = connection.cursor()

def table_setup():
    # Task: Check if the existing table signature is the same as the table we are trying to create
    try:
        cursor.execute("""
        CREATE TABLE recipe(
            recipeid NUMBER PRIMARY KEY,
            username VARCHAR2(25),
            parent NUMBER,
            location VARCHAR2(255),
            vegetarianism VARCHAR2(15),
            taste VARCHAR2(15),
            description VARCHAR2(255)
        )
        """)

        cursor.execute("""
        CREATE TABLE ingredients_lists(
            ingredient_id NUMBER,
            quantity NUMBER,
            recipe_id NUMBER,
            PRIMARY KEY (ingredient_id, recipe_id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id),
            FOREIGN KEY (recipe_id) REFERENCES recipe(recipeid)
        )
        """)

        cursor.execute("""
        CREATE TABLE ingredient(
            ingredient_id NUMBER PRIMARY KEY,
            name VARCHAR2(255)
        )
        """)
    except oracledb.DatabaseError as e:
        error, = e.args
        if error.code == 955:
            #print("Table stocks already exists.")
            pass
        else:
            raise

class Unique(Resource):
    parser = reqparse.RequestParser()  
    parser.add_argument('username', required=True) 
    parser.add_argument('parent', required=True)
    parser.add_argument('location', required=True)
    parser.add_argument('vegetarianism', required=True)
    parser.add_argument('taste', required=True)
    parser.add_argument('description', required=True)

    def get(self):  # Add the self argument here
        # Query to retrieve details of recipes without a parent
        query = "SELECT * FROM recipe WHERE parent IS NULL"
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all the results
        recipes = cursor.fetchall()
        
        return recipes


class Parent(Resource):
    parser = reqparse.RequestParser()  
    parser.add_argument('username', required=True) 
    parser.add_argument('parent', required=True)
    parser.add_argument('location', required=True)
    parser.add_argument('vegetarianism', required=True)
    parser.add_argument('taste', required=True)
    parser.add_argument('description', required=True)

    
    def get(recipe_id):
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

class Fork(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('recipeid', type=int, required=True, help='Recipe ID is required')
    parser.add_argument('username', type=str, required=True, help='Username is required')
    
    def post(self):
        args = self.parser.parse_args()
        
        # Check if the provided recipe ID exists
        cursor.execute("SELECT * FROM recipe WHERE recipeid = ?", (args['recipeid'],))
        existing_recipe = cursor.fetchone()
        if not existing_recipe:
            return {'error': 'Recipe does not exist'}, 404
        
        # Insert a new record into the recipe table with the provided username as the owner
        cursor.execute("""
            INSERT INTO recipe (recipeid, username, parent, location, vegetarianism, taste, description) 
            SELECT recipeid_seq.NEXTVAL, :username, parent, location, vegetarianism, taste, description
            FROM recipe
            WHERE recipeid = :recipeid
        """, {'username': args['username'], 'recipeid': args['recipeid']})
        
        # Commit the transaction
        connection.commit()
        
        return {'message': 'Recipe forked successfully'}, 201

class Edit(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('recipeid', type=int, required=True, help='Recipe ID is required')
    parser.add_argument('username', type=str, required=True, help='Username is required')
    parser.add_argument('location', type=str, required=True, help='Location is required')
    parser.add_argument('vegetarianism', type=str, required=True, help='Vegetarianism is required')
    parser.add_argument('taste', type=str, required=True, help='Taste is required')
    parser.add_argument('description', type=str, required=True, help='Description is required')

    def put(self):
        args = self.parser.parse_args()

        # Check if the provided recipe ID exists
        cursor.execute("SELECT * FROM recipe WHERE recipeid = ?", (args['recipeid'],))
        existing_recipe = cursor.fetchone()
        if not existing_recipe:
            return {'error': 'Recipe does not exist'}, 404

        # Update the recipe details
        cursor.execute("""
            UPDATE recipe
            SET username = :username, location = :location, vegetarianism = :vegetarianism,
                taste = :taste, description = :description
            WHERE recipeid = :recipeid
        """, args)
        
        # Commit the transaction
        connection.commit()

        return {'message': 'Recipe updated successfully'}, 200


class Pull(Resource):
    def get(self):
        # Query to retrieve all recipes
        cursor.execute("SELECT * FROM recipe")
        recipes = cursor.fetchall()
        
        return {'recipes': recipes}, 200


class Get(Resource):
    def get(self, recipeid):
        # Query to retrieve the details of a specific recipe
        cursor.execute("SELECT * FROM recipe WHERE recipeid = ?", (recipeid,))
        recipe = cursor.fetchone()
        
        if not recipe:
            return {'error': 'Recipe not found'}, 404
        
        return {'recipe': recipe}, 200
    

api.add_resource(Unique, '/posts')
api.add_resource(Parent, '/view_variation/<recipeid>')
api.add_resource(Fork, '/fork')
api.add_resource(Edit, '/edit')
api.add_resource(Pull, '/pull')
api.add_resource(Get, '/get/<int:recipeid>')


if __name__ == "__main__":
    table_setup()
    app.run(debug=True, host='0.0.0.0')
