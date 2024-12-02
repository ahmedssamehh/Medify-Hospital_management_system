// Login form submission
document.querySelector('#login form').addEventListener('submit', function (e) {
    e.preventDefault();
    const email = document.querySelector('#email').value.trim();
    const password = document.querySelector('#password').value.trim();

    if (!email || !password) {
        alert('Please fill in all fields!');
    } else {
        alert(`Welcome! Login successful for: ${email}`);
    }
});

// Registration form submission
document.querySelector('#register form')?.addEventListener('submit', function (e) {
    e.preventDefault();
    const name = document.querySelector('#name').value.trim();
    const email = document.querySelector('#emailReg').value.trim();
    const password = document.querySelector('#passwordReg').value.trim();

    if (!name || !email || !password) {
        alert('All fields are required!');
    } else {
        alert(`Welcome, ${name}! Registration complete.`);
    }
});

// Appointment booking
document.querySelector('#appointments form')?.addEventListener('submit', function (e) {
    e.preventDefault();
    const doctor = document.querySelector('#doctor').value;
    const date = document.querySelector('#date').value;

    if (!doctor || !date) {
        alert('Please select a doctor and date!');
    } else {
        alert(`Appointment booked with Doctor ID: ${doctor} on ${date}.`);
    }
});
