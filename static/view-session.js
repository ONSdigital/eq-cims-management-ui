const sessionId = localStorage.getItem("session_id") || crypto.randomUUID();
localStorage.setItem("session_id", sessionId);

const socket = io({ transports: ["polling", "websocket"], auth: { session_id: sessionId } });

socket.on("cell_update", (data) => {
  const statusCell = document.getElementById(data.guid).cells[data.index];
  statusCell.innerHTML = `<a href='result/${data.guid}' data-testid='ci-status-link-${data.guid}'>` +
    `<span class='ons-status ons-status--${data.suffix}'>${data.status}</span></a>`;
});

socket.on("buttons_disable", () => {
  const republishBtn = document.getElementById("republish-btn");
  const homeBtn = document.getElementById("home-btn");
  if (republishBtn) {
    republishBtn.classList.add("ons-btn--disabled");
    republishBtn.setAttribute("disabled", "");
  }
  if (homeBtn) {
    homeBtn.classList.add("ons-btn--disabled");
    homeBtn.setAttribute("disabled", "");
  }
});

socket.on("button_home_enable", () => {
  const homeBtn = document.getElementById("home-btn");
  if (homeBtn) {
    homeBtn.classList.remove("ons-btn--disabled");
    homeBtn.removeAttribute("disabled");
  }
});

socket.on("button_republish_enable", () => {
  const republishBtn = document.getElementById("republish-btn");
  if (republishBtn) {
    republishBtn.classList.remove("ons-btn--disabled");
    republishBtn.removeAttribute("disabled");
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const republishBtn = document.getElementById("republish-btn");
  if (republishBtn) {
    republishBtn.addEventListener("click", republish);
  }
});

function republish() {
  socket.emit("republish");
}
