document.addEventListener("DOMContentLoaded", () => {
  const createSessionBtn = document.getElementById("create-session-btn");
  createSessionBtn.addEventListener("click", clearSession);
});

function clearSession() {
  console.log("Clearing session data...");
  localStorage.clear();
}
