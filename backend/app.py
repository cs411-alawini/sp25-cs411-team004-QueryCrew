from flask import Flask, jsonify, request, send_from_directory, render_template

import mysql.connector

import random

from mysql.connector import Error

import os

from datetime import datetime, timedelta

 

# Static files for frontend (JavaScript)

app = Flask(__name__, template_folder='frontend', static_folder=os.path.join(os.path.dirname(__file__), 'static'))

 

print(f"Static folder path: {app.static_folder}")

 

# MySQL connection setup

def get_db():

    try:

        conn = mysql.connector.connect(

            host='34.57.170.47',  # Your MySQL host

            user='sharonchristelda@gmail.com',  # Your MySQL username

            password='QueryCrew',  # Your MySQL password

            database='RentalDB'  # The name of your database

        )

        if conn.is_connected():

            return conn

    except Error as e:

        print(f"Error: {e}")

        return None

 

# API route to retrieve all rentals

@app.route('/rentals', methods=['GET'])

def get_rentals():

    conn = get_db()

    if conn:

        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM Rentals')

        rentals = cursor.fetchall()

        conn.close()

        return jsonify(rentals)

    else:

        return jsonify({'error': 'Unable to connect to database'}), 500

 

# Route to serve the HTML page from frontend/ folder

@app.route('/')

def home():

    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))

    return send_from_directory(frontend_path, 'index.html')

 

@app.route('/city_selection')

def city_selection():

    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))

    return send_from_directory(frontend_path, 'city_selection.html')

 

# Serve static files (JS, CSS) from the frontend folder

@app.route('/js/<path:filename>')

def serve_js(filename):

    return send_from_directory('frontend/js', filename)

 

@app.route('/css/<path:filename>')

def serve_css(filename):

    return send_from_directory('backend/static/css', filename)

 

@app.route('/rent_form')

def rent_form():

    return send_from_directory('../frontend', 'rent_form.html')

 

@app.route('/after_rental')

def after_rental():

    return send_from_directory('../frontend', 'after_rental.html')

 

@app.route('/submit_rental', methods=['POST'])

def submit_rental():

    try:

        data = request.get_json()

        print("Received data:", data)

 

        # Validate customer_id

        customer_id = data.get('customer_id')

        if customer_id is None or customer_id == 'null' or not customer_id.isdigit():

            return jsonify({'success': False, 'error': 'Invalid or missing CustomerId'}), 400

 

        customer_id = int(customer_id)  # Convert to integer if it's a valid customer_id

 

        conn = get_db()

        cur = conn.cursor()

 

        rental_id = None

        while True:

            temp_id = random.randint(1, 39999)

            cur.execute("SELECT 1 FROM Rentals WHERE RentalId = %s", (temp_id,))

            if not cur.fetchone():

                rental_id = temp_id

                break

        print("Rental_id:", rental_id)

 

        # Insert into Rentals

        cur.execute("""

            INSERT INTO Rentals (RentalId, CarId, CustomerId, StartTime, EndTime, GarageId, TotalCost, Miles, Purpose)

            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)

        """, (

            rental_id,

            data['car_id'],

            customer_id,  # Valid customer_id

            data['start'],

            data['end'],

            data['pickup_garage_id'],

            data['total_cost'],

            data['miles'],

            data['purpose']

        ))

 

        # Update CarData garage id

        cur.execute("""

            UPDATE CarData

            SET GarageId = %s

            WHERE CarId = %s

        """, (

            data['dropoff_garage_id'],

            data['car_id']

        ))

 

        # Insert into CustomerSatisfaction table

        cur.execute("""

            INSERT INTO CustomerSatisfaction (RentalId, CustomerId, Rating, Comments)

            VALUES (%s, %s, %s, %s)

        """, (

            rental_id,

            customer_id,  # Valid customer_id

            data['rating'],

            data['comments']

        ))

 

        conn.commit()

        return jsonify({'success': True})

 

    except Exception as e:

        print("Error:", e)

        conn.rollback()

        return jsonify({'success': False, 'error': str(e)})

 

       

@app.route('/garages_by_city', methods=['GET'])

def garages_by_city():

    city = request.args.get('city')

    conn = get_db()

    if conn:

        cursor = conn.cursor(dictionary=True)

        query = """

            SELECT Garages.GarageId

            FROM Garages

            JOIN GarageLocation ON

                Garages.Latitude = GarageLocation.Latitude AND

                Garages.Longitude = GarageLocation.Longitude

            WHERE GarageLocation.City = %s

        """

        cursor.execute(query, (city,))

        garages = cursor.fetchall()

        cursor.close()

        conn.close()

        return jsonify(garages)

    else:

        return jsonify({'error': 'Unable to connect to database'}), 500

 

# # Login route to authenticate customers and businesses

# @app.route('/login', methods=['POST'])

# def login():

#     data = request.get_json()

#     user_type = data['userType']

#     user_id = data['userId']

#     conn = get_db()

#     cursor = conn.cursor()

 

#     if user_type == 'customer':

#         cursor.execute('SELECT * FROM Customers WHERE CustomerId = %s', (user_id,))

#     else:

#         cursor.execute('SELECT * FROM Garages WHERE GarageId = %s', (user_id,))

 

#     result = cursor.fetchone()

#     cursor.close()

#     conn.close()

 

#     if result:

#         if user_type == 'customer':

#             return jsonify({'message': 'Login successful', 'user_type': 'customer', 'user_id': user_id}), 200

#         else:

#             return jsonify({'message': 'Login successful', 'user_type': 'business'}), 200

#     else:

#         return jsonify({'error': 'Invalid ID'}), 401

@app.route('/login', methods=['POST'])

def login():

    data = request.get_json()

    user_type = data['userType']

    user_id = data['userId']

   

    conn = get_db()

    cursor = conn.cursor()

 

    if user_type == 'customer':

        cursor.execute('SELECT * FROM Customers WHERE CustomerId = %s', (user_id,))

    else:

        cursor.execute('SELECT * FROM Garages WHERE GarageId = %s', (user_id,))

 

    result = cursor.fetchone()

    cursor.close()

    conn.close()

 

    if result:

        if user_type == 'customer':

            return jsonify({

                'message': 'Login successful',

                'user_type': 'customer',

                'customer_id': user_id,

                'redirect_to': '/customer'  # Redirect URL here

            }), 200

        else:

            return jsonify({'message': 'Login successful', 'user_type': 'business'}), 200

    else:

        return jsonify({'error': 'Invalid ID'}), 401

   

# Route to get customer data

@app.route('/customer_data/<customer_id>', methods=['GET'])

def get_customer_data(customer_id):

    conn = get_db()  # Make sure your DB connection function is working

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Customers WHERE CustomerId = %s", (customer_id,))

    customer_data = cursor.fetchone()  # Fetch a single customer record

    if customer_data:

        return jsonify({

            'Name': customer_data['Name'],

            'Email': customer_data['Email'],

            'PhoneNumber': customer_data['PhoneNumber'],

            'Age': customer_data['Age']

        })

    else:

        return jsonify({'error': 'Customer not found'}), 404

 

@app.route('/profile')

def profile():

    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))

    print("Frontend path:", frontend_path)  # Debugging line

    return send_from_directory(frontend_path, 'profile.html')

 

@app.route('/update_profile', methods=['POST'])

def update_profile():

    try:

        data = request.get_json()  # Expecting a JSON body

        customer_id = data['customer_id']

        name = data['name']

        email = data['email']

        phone = data['phone']

        age = data['age']

 

        conn = get_db()  # Make sure your DB connection function is working

        cursor = conn.cursor()

        cursor.execute("""

            UPDATE Customers

            SET Name = %s, Email = %s, PhoneNumber = %s, Age = %s

            WHERE CustomerId = %s

        """, (name, email, phone, age, customer_id))

        conn.commit()

        cursor.close()

        conn.close()

        return jsonify({'success': True})

    except Exception as e:

        print("Error:", e)

        return jsonify({'success': False, 'error': str(e)}), 500

 

# API route for available vehicles based on the selected city

@app.route('/available_vehicles', methods=['GET'])

def available_vehicles():

    city = request.args.get('city')

    customer_id = request.args.get('customer_id')  # Optional but currently unused

    conn = get_db()

    if conn:

       

        cursor = conn.cursor(dictionary=True)

        query = '''

            SELECT CarData.CarId, CarData.Make, CarData.Model, CarData.Year, CarData.HourlyRate, CarData.GarageId

            FROM CarData

            JOIN Garages ON CarData.GarageId = Garages.GarageId

            JOIN GarageLocation ON

                Garages.Latitude = GarageLocation.Latitude AND

                Garages.Longitude = GarageLocation.Longitude

            WHERE GarageLocation.City = %s AND CarData.Availability = 1

        '''

        cursor.execute(query, (city,))

        results = cursor.fetchall()

        cursor.close()

        conn.close()

 

        if results:

            return jsonify(results)

        else:

            return jsonify([])  # Return an empty list so frontend handles it cleanly

    else:

        return jsonify({'error': 'DB connection failed'}), 500

 

# Serve the customer home page (for after login and city selection)

@app.route('/customer')

def customer_page():

    return send_from_directory('../frontend', 'customer_home.html')

 

# Route to add a rental (not yet implemented)

def add_rental():

    new_rental = request.get_json()  # Expecting JSON body in POST request

    conn = get_db()

    if conn:

        cursor = conn.cursor()

        cursor.execute('''

            INSERT INTO Rentals (CarId, CustomerId, StartTime, EndTime, GarageId, TotalCost, Miles, Purpose)

            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)

        ''', (new_rental['CarId'], new_rental['CustomerId'], new_rental['StartTime'],

              new_rental['EndTime'], new_rental['GarageId'], new_rental['TotalCost'],

              new_rental['Miles'], new_rental['Purpose']))

        conn.commit()

        conn.close()

        return jsonify({'message': 'Rental added successfully'}), 201

    else:

        return jsonify({'error': 'Unable to connect to database'}), 500

 

@app.route('/cities', methods=['GET'])

def get_cities():

    conn = get_db()

    if conn:

        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT City FROM GarageLocation")

        cities = [row[0] for row in cursor.fetchall()]

        cursor.close()

        conn.close()

        return jsonify(cities)

    else:

        return jsonify({'error': 'Unable to connect to database'}), 500

   

if __name__ == '__main__':

    app.run(debug=True)