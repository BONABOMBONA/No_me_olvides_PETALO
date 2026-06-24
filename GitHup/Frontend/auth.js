const API = "http://127.0.0.1:4000";

async function loginReal(email, password) {
  try {
    const res = await fetch(`${API}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ correo: email, contrasena: password })
    });
    if (!res.ok) {
      const err = await res.json();
      return { error: err.detail };
    }
    const data = await res.json();
    localStorage.setItem("token", data.token);
    localStorage.setItem("rol", data.rol);
    localStorage.setItem("nombre", data.nombre);
    
    const dashboards = {
      director: "dashboard-director.html",
      coordinador: "dashboard-director.html",
      psicologo: "dashboard-equipo.html",
      doctor: "dashboard-equipo.html",
      abogado: "dashboard-equipo.html",
      trabajador_social: "dashboard-equipo.html",
      analista: "dashboard-equipo.html",
      donante: "dashboard-donante.html",
    };
    return { dashboard: dashboards[data.rol] || "dashboard-equipo.html" };
  } catch(e) {
    return { error: "No se pudo conectar con el servidor" };
  }
}

function getToken()  { return localStorage.getItem("token"); }
function getRol()    { return localStorage.getItem("rol"); }
function getNombre() { return localStorage.getItem("nombre"); }

function getBase() {
  return ""; 
}
function logout() {
  localStorage.clear();
  window.location.href = getBase() + "index.html";
}

function requireAuth() {
  if (!getToken()) window.location.href = getBase() + "index.html";
}

function requireDirector() {
  const rol = getRol();
  if (!rol || !["director","coordinador"].includes(rol)) {
    window.location.href = getBase() + "index.html";
  }
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${getToken()}`
  };
}

function renderSidebar(activo) {
  const rol = getRol();
  const nombre = getNombre();
  const esDirector = ["director","coordinador"].includes(rol);
  const esDonante = rol === "donante";
  const base = getBase();

  const navDirector = esDirector ? `
    <div class="nav-label">Gestión</div>
    <div class="nav-item ${activo==='usuarios'?'active':''}" onclick="location.href='${base}lista-usuarios.html'">
      <span class="nav-icon">👥</span> Personal
    </div>
    <div class="nav-item ${activo==='invitaciones'?'active':''}" onclick="location.href='${base}dashboard-director.html'">
      <span class="nav-icon">🔗</span> Generar Link
    </div>` : "";

  const navNNA = !esDonante ? `
    <div class="nav-label">Beneficiarios</div>
    <div class="nav-item ${activo==='nna'?'active':''}" onclick="location.href='${base}lista-nna.html'">
      <span class="nav-icon">📋</span> Expedientes NNA
    </div>` : "";

  const navStats = esDirector || esDonante ? `
    <div class="nav-label">Reportes</div>
    <div class="nav-item ${activo==='stats'?'active':''}" onclick="location.href='${base}estadisticas.html'">
      <span class="nav-icon">📊</span> Estadísticas
    </div>` : "";

  const dashboardUrl = esDonante
    ? `${base}dashboard-donante.html`
    : esDirector
      ? `${base}dashboard-director.html`
      : `${base}dashboard-equipo.html`;

  return `
    <div class="sb-logo">
      <div class="sb-logo-icon">💠</div>
      <div>
        <div class="sb-logo-name">No Me Olvides</div>
        <div class="sb-logo-sub">Fundación Infantil</div>
      </div>
    </div>
    <div class="sb-user">
      <div class="sb-avatar">${nombre?nombre[0]:'U'}</div>
      <div>
        <div class="sb-uname">${nombre||'Usuario'}</div>
        <div class="sb-urole">${rol||''}</div>
      </div>
    </div>
    <nav class="sb-nav">
      <div class="nav-item ${activo==='dashboard'?'active':''}" onclick="location.href='${dashboardUrl}'">
        <span class="nav-icon">🏠</span> Inicio
      </div>
      ${navDirector}${navNNA}${navStats}
    </nav>
    <div class="sb-footer">
      <button class="btn-logout" onclick="logout()">🚪 Cerrar sesión</button>
    </div>`;
}
