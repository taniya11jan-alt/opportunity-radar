const API = "http://127.0.0.1:8000";

function getSession() {
  const token = localStorage.getItem("token");
  if (!token) return null;
  return {
    token,
    name: localStorage.getItem("name") || "",
    isAdmin: localStorage.getItem("isAdmin") === "1",
  };
}

function saveSession(data) {
  localStorage.setItem("token", data.token);
  localStorage.setItem("name", data.name);
  localStorage.setItem("isAdmin", data.is_admin ? "1" : "0");
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("name");
  localStorage.removeItem("isAdmin");
  location.href = "login.html";
}

// fetch() that sends the token. If the server says 401, the session is
// over, so we clear it and go to the login page.
async function authFetch(path, options = {}) {
  const s = getSession();
  const headers = Object.assign({}, options.headers || {});
  if (s) headers["Authorization"] = "Bearer " + s.token;
  const res = await fetch(API + path, Object.assign({}, options, { headers }));
  if (res.status === 401) {
    ["token", "name", "isAdmin"].forEach((k) => localStorage.removeItem(k));
    location.href = "login.html";
    throw new Error("Not logged in");
  }
  return res;
}

// Redirects away if the user should not be on this page.
function requireLogin(adminOnly = false) {
  const s = getSession();
  if (!s) {
    location.href = "login.html";
    return false;
  }
  if (adminOnly && !s.isAdmin) {
    location.href = "matches.html";
    return false;
  }
  return true;
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

// Fills <ul class="nav nav-pills" id="nav"></ul> for the current user.
function renderNav(active) {
  const s = getSession();
  const items = [["index.html", "Home", "home"]];
  if (s) items.push(["matches.html", "My Matches", "matches"]);
  if (s) items.push(["profile.html", "Profile", "profile"]);
  if (s && s.isAdmin) items.push(["admin.html", "Admin", "admin"]);
  if (!s) {
    items.push(["login.html", "Log in", "login"]);
    items.push(["signup.html", "Sign Up", "signup"]);
  }
  let html = items
    .map(
      ([href, label, key]) =>
        `<li class="nav-item"><a class="nav-link${key === active ? " active" : ""}" href="${href}">${label}</a></li>`,
    )
    .join("");
  if (s) {
    html += `<li class="nav-item"><a class="nav-link" href="#" onclick="logout(); return false;">Log out (${esc(s.name.split(" ")[0])})</a></li>`;
  }
  document.getElementById("nav").innerHTML = html;
}
