from flask import Flask
from flask_restful import Resource, Api, reqparse
import oracledb
import datetime
import dateutil.relativedelta
import math

# Credits: https://github.com/JustTheCoolest/StockAnalyser

app = Flask(__name__)
api = Api(app)
parent_and_siblings = []
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

class Analyser(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('price_at_buy', type=float, required=True)
    parser.add_argument('purchase_date', type=lambda string: datetime.datetime.strptime(string, '%Y-%m-%d').date(), required=True)
    parser.add_argument('fee_ratio_at_buy', type=float, required=True)
    parser.add_argument('fee_ratio_at_sell', type=float, required=True)
    parser.add_argument('capital_gains_tax_ratio', type=float, required=True)
    parser.add_argument('target_profit_ratio', type=float, required=True)
    
    def get(self, stock_name = None):
        if stock_name == None:
            cursor.execute('SELECT name FROM Stocks')
            return {'Available Stocks': cursor.fetchall()}
        cursor.execute(f"SELECT * FROM Stocks WHERE name = '{stock_name}'")
        stock_data = cursor.fetchall()
        if not stock_data:
            return {'message': 'Stock not found'}, 404
        # price_to_sell_with_strict_target, price_to_sell_with_year_target = 
        return [Analyser.target_sale_prices(*stock_data_row[1:]) for stock_data_row in stock_data]


    def post(self, stock_name):
        arguments = Analyser.parser.parse_args()
        cursor.execute(f"""
            INSERT INTO Stocks VALUES (
                '{stock_name}', 
                {arguments['price_at_buy']}, 
                TO_DATE('{arguments['purchase_date']}', 'yyyy-mm-dd'), 
                {arguments['fee_ratio_at_buy']}, 
                {arguments['fee_ratio_at_sell']}, 
                {arguments['capital_gains_tax_ratio']}, 
                {arguments['target_profit_ratio']}
            )
        """)
        connection.commit()
        return {'message': 'Stock added'}, 201

class Recipe(Resource):


    def unique():
        
        # Query to retrieve details of recipes without a parent
        query = "SELECT * FROM recipe WHERE parent IS NULL"
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all the results
        recipes = cursor.fetchall()
        
        return recipes
    
    def find_parents_and_siblings(recipe_id):


        def recursive_query(recipe_id):
            cursor.execute(f"SELECT recipeid FROM recipe WHERE parent = {recipe_id}")
            results = cursor.fetchall()
            for row in results:
                parent_and_siblings.append(row[0])
                recursive_query(row[0])
        
        # Call the recursive function to find parents and siblings
        recursive_query(recipe_id)
        
        
        return parent_and_siblings



    def post(self, stock_name):
        arguments = Analyser.parser.parse_args()
        cursor.execute(f"""
            INSERT INTO Stocks VALUES (
                '{stock_name}', 
                {arguments['price_at_buy']}, 
                TO_DATE('{arguments['purchase_date']}', 'yyyy-mm-dd'), 
                {arguments['fee_ratio_at_buy']}, 
                {arguments['fee_ratio_at_sell']}, 
                {arguments['capital_gains_tax_ratio']}, 
                {arguments['target_profit_ratio']}
            )
        """)
        connection.commit()
        return {'message': 'Stock added'}, 201



api.add_resource(Analyser, '/', '/<string:stock_name>')


if __name__ == "__main__":
    table_setup()
    app.run(debug=True, host='0.0.0.0')
