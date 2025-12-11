console.log("app.js loaded");

// ============================================================
// 0. ЗАХИСТ МАРШРУТІВ
// ============================================================
(function checkAccess() {
  const path = window.location.pathname;
  const token = localStorage.getItem("token");
  if (path.startsWith("/admin") && !token) {
    window.location.href = "/login";
  }
})();

// ============================================================
// 1. ФУНКЦІЯ ВИХОДУ
// ============================================================
async function logout() {
  console.warn("Performing full logout...");

  try {
    await fetch("/auth/logout");
  } catch (e) {
    console.error("Server logout failed", e);
  }

  localStorage.clear();
  sessionStorage.clear();

  const cookies = document.cookie.split(";");
  cookies.forEach((cookie) => {
    const eqPos = cookie.indexOf("=");
    const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
    document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
    document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
  });

  window.location.href = "/login";
}

// ============================================================
// 2. FETCH INTERCEPTOR
// ============================================================
const originalFetch = window.fetch;
window.fetch = async function (url, options = {}) {
  const token = localStorage.getItem("token");
  if (token)
    options.headers = { ...options.headers, Authorization: "Bearer " + token };

  const response = await originalFetch(url, options);
  if (response.status === 401 && !url.includes("/login")) logout();
  return response;
};

// ============================================================
// 3. UI UPDATE (Кнопки)
// ============================================================
function updateAuthUI() {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");
  const topbarRight = document.querySelector(".topbar-right");

  if (!token) {
    if (role) localStorage.clear();
    return;
  }

  if (token && topbarRight) {
    if (role === "admin" && !document.getElementById("admin-btn")) {
      const btn = document.createElement("a");
      btn.id = "admin-btn";
      btn.href = "/admin";
      btn.innerText = "🔥 Admin Panel";
      btn.style.cssText =
        "background:#ff4444;color:white;padding:8px 12px;border-radius:20px;font-weight:bold;text-decoration:none;margin-right:10px;";
      topbarRight.prepend(btn);
    }
    if (!document.getElementById("logout-btn")) {
      const logoutBtn = document.createElement("a");
      logoutBtn.id = "logout-btn";
      logoutBtn.href = "#";
      logoutBtn.innerText = "Вийти";
      logoutBtn.style.cssText =
        "color:#ccc;margin-left:15px;font-size:14px;cursor:pointer;text-decoration:underline;";
      logoutBtn.addEventListener("click", (e) => {
        e.preventDefault();
        logout();
      });
      topbarRight.appendChild(logoutBtn);
    }
  }
}
document.addEventListener("DOMContentLoaded", updateAuthUI);

// ============================================================
// 4. LOGIN
// ============================================================
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    localStorage.clear();
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    const out = document.getElementById("loginStatus");
    if (res.ok) {
      localStorage.setItem("token", data.token);
      localStorage.setItem("role", data.role);
      document.cookie = `token=${data.token}; path=/; max-age=3600`;
      window.location.href = "/";
    } else {
      out.innerText = "Помилка: " + data.detail;
    }
  });
}

// ============================================================
// 5. REGISTER
// ============================================================
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

// ============================================================
// 6. PRODUCTS LIST (З обробкою картинок)
// ============================================================
const productsContainer = document.getElementById("products");
const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("searchQuery");
const searchInfo = document.getElementById("searchInfo");

async function loadProducts(query = "") {
  if (!productsContainer) return;
  let url = "/products";
  if (query && query.trim() !== "")
    url += "?q=" + encodeURIComponent(query.trim());

  try {
    const res = await fetch(url);
    if (res.status === 401) return;
    const data = await res.json();
    productsContainer.innerHTML = "";

    if (!Array.isArray(data) || data.length === 0) {
      productsContainer.innerHTML = "<p>Нічого не знайдено.</p>";
      if (searchInfo) searchInfo.innerText = query ? `Results: 0` : "";
      return;
    }

    if (searchInfo)
      searchInfo.innerText = query
        ? `Results: ${data.length}`
        : `Total: ${data.length}`;

    data.forEach((p) => {
      const card = document.createElement("article");
      card.className = "product-card";

      // Логіка відображення картинок
      let imgFile = p.image || "523634223.webp";
      if (!imgFile.startsWith("/") && !imgFile.startsWith("http")) {
        imgFile = "/static/img/" + imgFile;
      }

      // XSS тут залишено навмисно
      card.innerHTML = `
                <img src="${imgFile}" alt="product" class="product-thumb">
                <b>${p.name}</b>
                <p class="product-desc">${p.description}</p>
                <a href="/product?id=${p.id}">Open</a>
            `;
      productsContainer.appendChild(card);
    });
  } catch (err) {
    console.error(err);
  }
}

if (searchForm) {
  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    loadProducts(searchInput ? searchInput.value : "");
  });
}
if (productsContainer) loadProducts();

// ============================================================
// 7. DEVELOPER TOOLS (Вразливість BAC)
// ============================================================
// TODO: Видалити цю функцію перед релізом! Вона дозволяє міняти ціни!
async function updateProduct(id, name, price) {
  console.log(`Updating product ${id}...`);
  const formData = new FormData();
  formData.append("id", id);
  formData.append("name", name);
  formData.append("price", price);

  // Відправляємо запит. Завдяки fetch interceptor, заголовок Authorization додасться сам.
  const res = await fetch("/product/update", {
    method: "POST",
    body: formData,
  });

  if (res.ok) {
    console.log("Success! Reloading page...");
    window.location.reload();
  } else {
    console.error("Error updating product. Check console/network.");
  }
}
