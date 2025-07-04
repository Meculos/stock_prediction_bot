document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('register_form').addEventListener('submit', (event) => {
        event.preventDefault()

        const email = document.getElementById('email').value;
        const username = document.getElementById('username').value;
        const password1 = document.getElementById('password1').value;
        const password2 = document.getElementById('password2').value;

        fetch('/api/v1/register/', {
            method: 'POST',
            body: JSON.stringify({
                'username': username,
                'email': email,
                'password': password1,
                'confirm_password': password2
            }),
            headers: {
                'content-type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                data.error.forEach(element => {
                    document.getElementById('errorMessages').innerHTML = element;
                });
            } else if (data.message) {
                document.getElementById('errorMessages').innerHTML = data.message;
                window.location.href = data.login_page;
            }
        })
        .catch(error => console.log('Error registering user: ', error))
    })

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
})