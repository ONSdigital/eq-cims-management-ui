const sessionId = localStorage.getItem("session_id") || crypto.randomUUID();
localStorage.setItem("session_id", sessionId);

const socket = io({ transports: ["polling"], auth: { session_id: sessionId } });

socket.on("cell_update", (data) => {
  const statusCell = document.getElementById(data.guid).cells[data.index];
  statusCell.innerHTML = `<a href='result/${data.guid}'><span class='ons-status ons-status--${data.suffix}'>${data.status}</span></a>`;
});

socket.on("button_disable", () => {
    const republishBtn = document.getElementById("republish-btn");
    if (republishBtn) {
        republishBtn.classList.add("ons-btn--disabled");
        republishBtn.setAttribute("disabled", "");
    }
  }
)

socket.on("button_enable", () => {
    const republishBtn = document.getElementById("republish-btn");
    if (republishBtn) {
        republishBtn.classList.remove("ons-btn--disabled");
        republishBtn.removeAttribute("disabled");
    }
});

document.addEventListener("DOMContentLoaded", () => {
  const republishBtn = document.getElementById("republish-btn");
  republishBtn.addEventListener("click", republish);
});

function republish() {
  socket.emit("republish");
}
