const form = document.getElementById('login-form');

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  // Here you can add your logic to handle the login process
  console.log('Username:', username);
  console.log('Password:', password);

  // You can add a redirect or display a success message
  alert('Login successful!');
});