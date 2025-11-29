console.log("app.js loaded");

///////////////////////////////////////////////////////////////////////////////
// Перехоплювач fetch — додає токен автоматично (слабка авторизація)
///////////////////////////////////////////////////////////////////////////////

const originalFetch = window.fetch;
window.fetch = async function (url, options = {}) {
    const token = localStorage.getItem("token");

    if (token) {
        options.headers = {
            ...(options.headers || {}),
            "Authorization": "Bearer " + token
        };
    }

    return originalFetch(url, options);
};

///////////////////////////////////////////////////////////////////////////////
// LOGIN
///////////////////////////////////////////////////////////////////////////////

const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const res = await fetch("/auth/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();
        const out = document.getElementById("loginStatus");

        if (res.ok) {
            // VULN: токен = username, лежить у localStorage без шифрування
            localStorage.setItem("token", data.token);
            out.innerText = "Успішний вхід!";
            window.location.href = "/";
        } else {
            out.innerText = "Помилка: " + data.detail;
        }
    });
}

///////////////////////////////////////////////////////////////////////////////
// REGISTER (через вразливий SQL /auth/register)
///////////////////////////////////////////////////////////////////////////////

const registerForm = document.getElementById("registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = document.getElementById("reg_username").value;
        const password = document.getElementById("reg_password").value;

        // VULN: бекенд будує SQL через f-рядки, можливий SQLi
        const res = await fetch("/auth/register", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();
        const out = document.getElementById("registerStatus");

        if (res.ok) {
            out.innerText = "Акаунт створено. Тепер можна увійти.";
        } else {
            out.innerText = "Помилка: " + data.detail;
        }
    });
}

///////////////////////////////////////////////////////////////////////////////
// PRODUCTS LIST + SEARCH
///////////////////////////////////////////////////////////////////////////////

const PRODUCTS_IMG = "/static/img/523634223.webp";
const productsContainer = document.getElementById("products");
const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("searchQuery");
const searchInfo = document.getElementById("searchInfo");

async function loadProducts(query = "") {
    if (!productsContainer) return;

    let url = "/products";
    if (query && query.trim() !== "") {
        // на бекенді теж без параметризації -> SQLi
        url += "?q=" + encodeURIComponent(query.trim());
    }

    try {
        const res = await fetch(url);
        const data = await res.json();

        productsContainer.innerHTML = "";

        if (!Array.isArray(data) || data.length === 0) {
            productsContainer.innerHTML = "<p>Нічого не знайдено.</p>";
            if (searchInfo) {
                searchInfo.innerText = query
                    ? `Результати пошуку для "${query}": 0`
                    : "";
            }
            return;
        }

        if (searchInfo) {
            searchInfo.innerText = query
                ? `Результати пошуку для "${query}" (знайдено: ${data.length})`
                : `Усього товарів: ${data.length}`;
        }

        data.forEach((p) => {
            const card = document.createElement("article");
            card.className = "product-card";

            // VULN: опис вставляється через innerHTML -> stored XSS з БД
            card.innerHTML = `
                <img src="${PRODUCTS_IMG}" alt="product" class="product-thumb">
                <b>${p.name}</b>
                <p class="product-desc">${p.description}</p>
                <a href="/product?id=${p.id}">Open</a>
            `;

            productsContainer.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load products:", err);
        if (searchInfo) {
            searchInfo.innerText = "Помилка завантаження товарів";
        }
    }
}

// Пошук з верхнього бару
if (searchForm && productsContainer) {
    searchForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const q = searchInput ? searchInput.value : "";
        loadProducts(q);
    });
}

// Автоматично підтягуємо товари при заході на головну
if (productsContainer) {
    loadProducts();
}
