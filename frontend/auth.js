const API = "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("token");
}
function isAdmin() {
  return localStorage.getItem("isAdmin") === "1";
}

function saveSession(d) {
  localStorage.setItem("token", d.token);
  localStorage.setItem("name", d.name);
  localStorage.setItem("isAdmin", d.is_admin ? "1" : "0");
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("name");
  localStorage.removeItem("isAdmin");
  location.href = "login.html";
}

function esc(s) {
  return String(s ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
}

function renderNav(active) {
  const items = [["index.html", "Home", "home"]];
  if (getToken()) items.push(["matches.html", "My Matches", "matches"]);
  if (getToken() && isAdmin()) items.push(["admin.html", "Admin", "admin"]);
  if (!getToken()) {
    items.push(
      ["login.html", "Login", "login"],
      ["signup.html", "Sign Up", "signup"],
    );
  }
  let html = items
    .map(
      ([href, label, key]) =>
        `<li class="nav-item"><a class="nav-link ${key === active ? "active" : ""}" href="${href}">${label}</a></li>`,
    )
    .join("");
  if (getToken()) {
    html += `<li class="nav-item"><a class="nav-link" href="#" onclick="logout(); return false;">Logout (${esc(localStorage.getItem("name"))})</a></li>`;
  }
  document.getElementById("nav").innerHTML = html;
}

// Authenticated request. Sends the token and logs out if it has expired.
async function api(path, options = {}) {
  const headers = Object.assign({}, options.headers, {
    Authorization: "Bearer " + getToken(),
  });
  const res = await fetch(API + path, Object.assign({}, options, { headers }));
  if (res.status === 401) {
    logout();
    throw new Error("Session expired");
  }
  return res;
}
