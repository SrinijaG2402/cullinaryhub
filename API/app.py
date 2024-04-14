from flask import Flask
from flask_restful import Resource, Api, reqparse
import oracledb
import datetime
import dateutil.relativedelta
import math

# Credits: https://github.com/JustTheCoolest/StockAnalyser

app = Flask(__name__)
api = Api(app)

connection = oracledb.connect(user='system', password=open('API/password.txt').read(), dsn='localhost:1521/xe')
cursor = connection.cursor()

def table_setup():
    # Task: Check if the existing table signature is the same as the table we are trying to create
    try:
        cursor.execute(
            '''
            CREATE TABLE Stocks(
            )
            ''')
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


api.add_resource(Analyser, '/', '/<string:stock_name>')

if __name__ == "__main__":
    table_setup()
    app.run(debug=True, host='0.0.0.0')
