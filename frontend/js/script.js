// Fetch and display all customers
async function fetchCustomers() {
    const response = await fetch('http://localhost:5000/customers');
    const customers = await response.json();
    const customersList = document.getElementById('customersList');
    customersList.innerHTML = ''; // Clear existing list

    customers.forEach(customer => {
        const listItem = document.createElement('li');
        listItem.textContent = `${customer.Name} - ${customer.Email}`;
        customersList.appendChild(listItem);
    });
}

// Add a new customer
async function addCustomer(event) {
    event.preventDefault();

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const age = document.getElementById('age').value;

    const response = await fetch('http://localhost:5000/customers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ Name: name, Email: email, PhoneNumber: phone, Age: age })
    });

    if (response.ok) {
        fetchCustomers(); // Refresh the customer list
    }
}

// Bind the form submit event
document.getElementById('addCustomerForm').addEventListener('submit', addCustomer);

// Load customers when the page is loaded
fetchCustomers();

let currentUser = {};


$('#loginForm').submit(function (e) {
    e.preventDefault();
    const userType = $('#userType').val();
    const userId = $('#userId').val();
  
    $.ajax({
      url: '/login',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ userType, userId }),
      success: function (response) {
        if (userType === 'customer') {
          window.location.href = `/customer?CustomerId=${userId}`;
        } else {
          window.location.href = `/business?GarageId=${userId}`;
        }
      },
      error: function () {
        alert('Login failed. Please check your ID.');
      }
    });
  });

  // Only run this part if on the city_selection page
if (window.location.pathname.includes('city_selection')) {
  const params = new URLSearchParams(window.location.search);
  const city = params.get('city');
  const customerId = params.get('customer_id');

  fetch(`/available_vehicles?city=${encodeURIComponent(city)}&customer_id=${customerId}`)
    .then(response => response.json())
    .then(vehicles => {
      const tableBody = document.getElementById('vehicleTableBody');
      if (!tableBody) return;

      vehicles.forEach(vehicle => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${vehicle.Make}</td>
          <td>${vehicle.Model}</td>
          <td>${vehicle.Year}</td>
          <td>$${vehicle.HourlyRate}</td>
          <td>
            <a class="btn btn-success" 
               href="/rent_form?car_id=${vehicle.CarId}&customer_id=${customerId}&rate=${vehicle.HourlyRate}">
              Rent
            </a>
          </td>
        `;
        tableBody.appendChild(row);
      });
    })
    .catch(err => {
      console.error('Error fetching vehicles:', err);
    });
}
