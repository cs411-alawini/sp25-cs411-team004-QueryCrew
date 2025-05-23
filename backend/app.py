from flask import Flask, jsonify, request, send_from_directory, render_template
import mysql.connector
import random
from mysql.connector import Error
import os
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='frontend', static_folder=os.path.join(os.path.dirname(__file__), 'static'))
print(f"Static folder path: {app.static_folder}")

def get_db():

    try:

        conn = mysql.connector.connect(
            host='34.57.170.47', 
            user='sharonchristelda@gmail.com', 
            password='QueryCrew', 
            database='RentalDB' 
        )

        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error: {e}")
        return None

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

 


@app.route('/')
def home():
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
    return send_from_directory(frontend_path, 'index.html')

 

@app.route('/city_selection')
def city_selection():
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
    return send_from_directory(frontend_path, 'city_selection.html')

 


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

        customer_id = int(customer_id) 
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
            customer_id,  
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

 
        rating = data.get('rating')
        comments = data.get('comments')

        if rating == '' or rating is None:
            rating = None
        else:
            rating = int(rating) 

        if comments == '':
            comments = None

        # Insert into CustomerSatisfaction table
        if 'rating' in data and 'comments' in data and data['rating'] is not None and data['comments'] is not None:
            cur.execute("""
                INSERT INTO CustomerSatisfaction (RentalId, CustomerId, Rating, Comments)
                VALUES (%s, %s, %s, %s)
            """, (
                rental_id,
                customer_id,  
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

 

@app.route('/login', methods=['POST'])

def login():

    data = request.get_json()
    user_type = data['userType']
    user_id = data['userId']

    conn = get_db()
    cursor = conn.cursor()

    result = None

    if user_type == 'customer':
        cursor.execute('SELECT * FROM Customers WHERE CustomerId = %s', (user_id,))
        result = cursor.fetchone()
    elif user_type == 'business' and user_id == '123456':  
        result = True 
    else:
        return jsonify({'error': 'Invalid ID'}), 401  

    cursor.close()
    conn.close()

    if result:
        if user_type == 'customer':
            return jsonify({
                'message': 'Login successful',
                'user_type': 'customer',
                'customer_id': user_id,
                'redirect_to': '/customer' 
            }), 200

        elif user_type == 'business' and user_id == '123456':
            return jsonify({
                'message': 'Business login successful',
                'user_type': 'business',
                'redirect_to': '/business_home'  
            }), 200

    else:
        return jsonify({'error': 'Invalid ID'}), 401

    
@app.route('/business_home', methods=['GET'])
def business_home():
    return send_from_directory('../frontend', 'business_home.html')


# Route to get customer data

@app.route('/customer_data/<customer_id>', methods=['GET'])

def get_customer_data(customer_id):

    conn = get_db()  
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Customers WHERE CustomerId = %s", (customer_id,))
    customer_data = cursor.fetchone() 
    if customer_data:
        return jsonify({
            'Name': customer_data['Name'],
            'Email': customer_data['Email'],
            'PhoneNumber': customer_data['PhoneNumber'],
            'Age': customer_data['Age']
        })

    else:
        return jsonify({'error': 'Customer not found'}), 404
@app.route('/customer_summary/<customer_id>', methods=['GET'])
def get_customer_summary(customer_id):

    try:
        customer_id = int(customer_id)
    except ValueError:
        return jsonify({'error': 'Invalid customer ID'}), 400

    conn = get_db()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.callproc('GetCustomerRentalSummaryById', [customer_id])

            for result in cursor.stored_results():
                summary = result.fetchall()

            cursor.close()
            conn.close()

            if summary:
                return jsonify(summary[0])  
            else:
                return jsonify({'error': 'No summary found for this customer'}), 404

        except Exception as e:
            print(f"Error during stored procedure call: {e}")
            return jsonify({'error': 'An error occurred while fetching the summary'}), 500
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

@app.route('/get_garages_by_city', methods=['POST'])
def get_garages_by_city():
    data = request.get_json()
    city = data.get('city')
    
    if not city:
        return jsonify({'error': 'City is required'}), 400
    
    conn = get_db() 
    conn.start_transaction(isolation_level='READ COMMITTED')
    cur = conn.cursor()

    # --- ADVANCED QUERY 1: Aggregate rentals per garage ---
    cur.execute("""
    SELECT g.GarageId, COUNT(r.RentalId) AS total_rentals
    FROM Garages g
    LEFT JOIN Rentals r ON g.GarageId = r.GarageId
    JOIN GarageLocation gl ON g.Latitude = gl.Latitude AND g.Longitude = gl.Longitude
    WHERE gl.City = %s
    GROUP BY g.GarageId
    """, (city,))
    
    garage_rental_counts = cur.fetchall()
    print("Garage rental counts:", garage_rental_counts)

    # --- ADVANCED QUERY 2: Rental with highest total cost for each garage ---
    cur.execute("""
    SELECT g.GarageId, r.RentalId, r.TotalCost
    FROM Rentals r
    JOIN CarData c ON r.CarId = c.CarId
    JOIN Garages g ON c.GarageId = g.GarageId
    JOIN GarageLocation gl ON g.Latitude = gl.Latitude AND g.Longitude = gl.Longitude
    WHERE gl.City = %s AND r.TotalCost = (
        SELECT MAX(r2.TotalCost)
        FROM Rentals r2
        JOIN CarData c2 ON r2.CarId = c2.CarId
        WHERE c2.GarageId = g.GarageId
    )
    ORDER BY g.GarageId
    """, (city,))

    highest_rentals = cur.fetchall()
    print("Rental with highest total cost for each garage:", highest_rentals)

    garage_info_dict = {}

    for row in garage_rental_counts:
        garage_info_dict[row[0]] = {'RentalCount': row[1], 'HighestRentalId': None}

    for row in highest_rentals:
        garage_info_dict[row[0]]['HighestRentalId'] = row[1]
    
    garages_info = []
    for garage_id, info in garage_info_dict.items():
        highest_rental_id = info['HighestRentalId']
        if highest_rental_id is None or info['RentalCount'] == 0:
            highest_rental_id = '--'  # Replace None with '--' for garages with 0 rentals

        garages_info.append({
            'GarageId': garage_id,
            'RentalCount': info['RentalCount'],
            'HighestRentalId': highest_rental_id
        })
    
    cur.close()
    conn.close()

    return jsonify({'garages': garages_info})

@app.route('/profile')
def profile():
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
    print("Frontend path:", frontend_path) 
    return send_from_directory(frontend_path, 'profile.html')

 

@app.route('/update_profile', methods=['POST'])
def update_profile():
    try:

        data = request.get_json() 
        customer_id = data['customer_id']
        name = data['name']
        email = data['email']
        phone = data['phone']
        age = data['age']

        conn = get_db() 
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

 

@app.route('/available_vehicles', methods=['GET'])

def available_vehicles():
    city = request.args.get('city')
    customer_id = request.args.get('customer_id') 
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
            return jsonify([])  
    else:
        return jsonify({'error': 'DB connection failed'}), 500


@app.route('/customer', methods=['GET'], strict_slashes=False)
def customer_page():
    return send_from_directory('../frontend', 'customer_home.html')

if __name__ == '__main__':
    app.run(debug=True)
