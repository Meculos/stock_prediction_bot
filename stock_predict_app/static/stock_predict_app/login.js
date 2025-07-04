document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('loginForm').addEventListener('submit', (event) => {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // First: Login via JWT
    fetch('/api/v1/token/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("Invalid credentials");
      }
      return response.json();
    })
    .then(data => {
      localStorage.setItem('access_stock_bot', data.access);
      localStorage.setItem('refresh_stock_bot', data.refresh);

      return fetch('/api/v1/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ username, password })
      });
    })
    .then(response => {
      if (!response.ok) throw new Error("Session login failed");
      return response.json();
    })
    .then(data => {
      if (data.error) {
        document.getElementById('errorMessages').innerText = data.error;
      } else {
        document.getElementById('errorMessages').innerText = data.message;
        window.location.href = data.dashboard || '/dashboard/';
      }
    })
    .catch(error => {
      document.getElementById('errorMessages').innerText = error.message;
    });
  });

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
