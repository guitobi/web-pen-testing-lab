console.log("app.js loaded");

// --- 1. Перехоплювач fetch (Авторизація для API) ---
const originalFetch = window.fetch;
window.fetch = async function (url, options = {}) {
  const token = localStorage.getItem("token");
  if (token) {
    options.headers = {
      ...(options.headers || {}),
      Authorization: "Bearer " + token,
    };
  }
  return originalFetch(url, options);
};

// --- 2. Логіка появи кнопки АДМІНА (Нове!) ---
function checkAdminButton() {
  const role = localStorage.getItem("role");
  const topbarRight = document.querySelector(".topbar-right");

  // Якщо ми адмін і знайшли праву частину шапки
  if (role === "admin" && topbarRight) {
    // Перевіряємо, чи кнопки ще немає (щоб не дублювати)
    if (!document.getElementById("admin-btn")) {
      const btn = document.createElement("a");
      btn.id = "admin-btn";
      btn.href = "/admin";
      btn.innerText = "🔥 Admin Panel";

      // Стилі прямо тут
      btn.style.backgroundColor = "#ff4444";
      btn.style.color = "white";
      btn.style.padding = "8px 12px";
      btn.style.borderRadius = "20px";
      btn.style.fontWeight = "bold";
      btn.style.textDecoration = "none";
      btn.style.marginRight = "10px";

      // Додаємо кнопку на початок блоку справа
      topbarRight.prepend(btn);
    }
  }
}

// Запускаємо перевірку при завантаженні сторінки
document.addEventListener("DOMContentLoaded", checkAdminButton);

// --- 3. LOGIN (Вхід) ---
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();
    const out = document.getElementById("loginStatus");

    if (res.ok) {
      // ЗБЕРІГАЄМО ТОКЕН І РОЛЬ
      localStorage.setItem("token", data.token);
      localStorage.setItem("role", data.role);

      // Встановлюємо куку для доступу до адмінки (ВАЖЛИВО!)
      document.cookie = `token=${data.token}; path=/; max-age=3600`;

      out.innerText = "Успішний вхід!";
      window.location.href = "/";
    } else {
      out.innerText = "Помилка: " + data.detail;
    }
  });
}

// --- 4. REGISTER (Реєстрація) ---
const registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("reg_username").value;
    const password = document.getElementById("reg_password").value;

    const res = await fetch("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    const out = document.getElementById("registerStatus");
    if (res.ok) out.innerText = "Акаунт створено. Тепер можна увійти.";
    else out.innerText = "Помилка: " + data.detail;
  });
}

// --- 5. PRODUCTS LIST (Список товарів + Пошук) ---
const PRODUCTS_IMG = "/static/img/523634223.webp";
const productsContainer = document.getElementById("products");
const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("searchQuery");
const searchInfo = document.getElementById("searchInfo");

async function loadProducts(query = "") {
  if (!productsContainer) return;
  let url = "/products";
  if (query && query.trim() !== "") {
    url += "?q=" + encodeURIComponent(query.trim());
  }
  try {
    const res = await fetch(url);
    const data = await res.json();
    productsContainer.innerHTML = "";

    if (!Array.isArray(data) || data.length === 0) {
      productsContainer.innerHTML = "<p>Нічого не знайдено.</p>";
      if (searchInfo)
        searchInfo.innerText = query ? `Результати для "${query}": 0` : "";
      return;
    }

    if (searchInfo) {
      searchInfo.innerText = query
        ? `Результати для "${query}" (${data.length})`
        : `Усього товарів: ${data.length}`;
    }

    data.forEach((p) => {
      const card = document.createElement("article");
      card.className = "product-card";
      // Тут залишається XSS вразливість для інших завдань (innerHTML)
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
  }
}

if (searchForm && productsContainer) {
  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    loadProducts(searchInput ? searchInput.value : "");
  });
}
if (productsContainer) {
  loadProducts();
}
