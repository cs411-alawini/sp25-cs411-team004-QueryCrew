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