const sessionId = localStorage.getItem("session_id") || crypto.randomUUID();
localStorage.setItem("session_id", sessionId);

const socket = io({ transports: ["polling"], auth: { session_id: sessionId } });
// Connection events
socket.on("connect", () => {
    console.log("Connected:", socket.id);
});

socket.on("cell_update", (data) => {
  const statusCell = document.getElementById(data.guid).cells[data.index];
  console.log(data.index)
  if (statusCell) {
    if (data.status === "Success") {
      statusCell.innerHTML = `<span class='ons-status ons-status--success'>${data.status}</span>`;
    } else if (data.status === "Started") {
      statusCell.innerHTML = `<span class='ons-status ons-status--info'>${data.status}</span>`;
    } else if (data.status === "Not Started") {
      statusCell.innerHTML = `<span class='ons-status ons-status--dead'>${data.status}</span>`;
    } else if (data.status === "Failure") {
      statusCell.innerHTML = `<span class='ons-status ons-status--error'>${data.status}</span>`;
    }
  }
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
