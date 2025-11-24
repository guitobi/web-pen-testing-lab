console.log("app.js loaded");

////////////////////////////////////////////////////////////////////////////////
// LOGIN
////////////////////////////////////////////////////////////////////////////////

const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const res = await fetch("/auth/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username, password})
        });

        const data = await res.json();
        const out = document.getElementById("loginStatus");

        if (res.ok) {
            localStorage.setItem("token", data.token);
            out.innerText = "Успішний вхід!";
            window.location.href = "/";
        } else {
            out.innerText = "Помилка: " + data.detail;
        }
    });
}

////////////////////////////////////////////////////////////////////////////////
// REGISTER
////////////////////////////////////////////////////////////////////////////////

const registerForm = document.getElementById("registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = document.getElementById("reg_username").value;
        const password = document.getElementById("reg_password").value;

        // Реєстрація через SQL-инъекцию endpoint
        const res = await fetch("/auth/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username, password})
        });

        const out = document.getElementById("registerStatus");

        if (res.ok) {
            out.innerText = "Акаунт створено!";
            window.location.href = "/login";
        } else {
            out.innerText = "Помилка: можливо, користувач вже існує.";
        }
    });
}

////////////////////////////////////////////////////////////////////////////////
// TOKEN ATTACH
////////////////////////////////////////////////////////////////////////////////

// Перехоплювач fetch — додає токен автоматично
const originalFetch = fetch;
window.fetch = async function(url, options = {}) {
    const token = localStorage.getItem("token");

    if (token) {
        options.headers = {
            ...(options.headers || {}),
            "Authorization": "Bearer " + token
        };
    }

    return originalFetch(url, options);
};