from flask import Flask, request, jsonify, render_template, redirect
import mysql.connector

app = Flask(__name__)

# Setup Database connection (adjust your credentials if needed)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="rental_db"   # Change to your database name
)

#########################################
# Customer + Business Login Route
#########################################
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_type = data.get('userType')
    user_id = data.get('userId')

    if user_type == 'customer':
        return jsonify({'user_type': 'customer'})
    elif user_type == 'business':
        return jsonify({'user_type': 'business'})
    else:
        return jsonify({'error': 'Invalid user type'}), 400

#########################################
# Cities for Customers
#########################################
@app.route('/cities', methods=['GET'])
def cities():
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT City FROM Garages")
    results = cursor.fetchall()
    cursor.close()

    cities_list = [row[0] for row in results]
    return jsonify(cities_list)

#########################################
# Available Vehicles for a selected City
#########################################
@app.route('/available_vehicles', methods=['GET'])
def available_vehicles():
    city = request.args.get('city')

    cursor = db.cursor(dictionary=True)
    query = """
    SELECT v.CarId, v.Make, v.Model, v.Year, v.HourlyRate, v.GarageId
    FROM Vehicles v
    JOIN Garages g ON v.GarageId = g.GarageId
    WHERE g.City = %s
    """
    cursor.execute(query, (city,))
    vehicles = cursor.fetchall()
    cursor.close()

    return jsonify(vehicles)

#########################################
# Customer Submit Rental
#########################################
@app.route('/submit_rental', methods=['POST'])
def submit_rental():
    data = request.get_json()
    
    cursor = db.cursor()
    query = """
    INSERT INTO Rentals (CarId, CustomerId, StartTime, EndTime, Purpose, MilesDriven, TotalCost, DropoffLocation, Rating, Comments, PickupGarageId)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        data['car_id'],
        data['customer_id'],
        data['start'],
        data['end'],
        data['purpose'],
        data['miles'],
        data['total_cost'],
        data['dropoff'],
        data['rating'],
        data['comments'],
        data['pickup_garage_id']
    ))
    db.commit()
    cursor.close()

    return jsonify({'message': 'Rental submitted successfully'})

#########################################
# BUSINESS SIDE ROUTES
#########################################

# Add New Vehicle
@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    data = request.get_json()

    cursor = db.cursor()
    query = """
    INSERT INTO Vehicles (GarageId, Make, Model, Year, HourlyRate)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        data['garage_id'],
        data['make'],
        data['model'],
        data['year'],
        data['hourly_rate']
    ))
    db.commit()
    cursor.close()

    return jsonify({'message': 'Vehicle added successfully'})

# Rental History for Business
@app.route('/rental_history_data', methods=['GET'])
def rental_history_data():
    garage_id = request.args.get('garage_id')

    cursor = db.cursor(dictionary=True)
    query = """
    SELECT CustomerId as customer_id, CarId as car_id, StartTime as start_time, EndTime as end_time, TotalCost as total_cost, Rating as rating
    FROM Rentals
    WHERE PickupGarageId = %s
    ORDER BY StartTime DESC
    """
    cursor.execute(query, (garage_id,))
    rentals = cursor.fetchall()
    cursor.close()

    return jsonify(rentals)

#########################################
# Home page to serve index.html
#########################################
@app.route('/')
def index():
    return render_template('index.html')

#########################################
# Serve HTML Pages
#########################################
@app.route('/city_selection')
def city_selection():
    return render_template('city_selection.html')

@app.route('/rent_form')
def rent_form():
    return render_template('rent_form.html')

@app.route('/after_rental')
def after_rental():
    return render_template('after_rental.html')

@app.route('/business_home')
def business_home():
    return render_template('business_home.html')

@app.route('/add_vehicle_page')
def add_vehicle_page():
    return render_template('add_vehicle.html')

@app.route('/rental_history')
def rental_history():
    return render_template('rental_history.html')

#########################################
# Start the Flask App
#########################################
if __name__ == '__main__':
    app.run(debug=True)
