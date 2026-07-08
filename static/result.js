const sessionId = localStorage.getItem("session_id") || crypto.randomUUID();
localStorage.setItem("session_id", sessionId);

const socket = io({ transports: ["polling"], auth: { session_id: sessionId } });

socket.on("cell_update", (data) => {
  const statusElement = document.getElementById(`result-${data.guid}`);
  if (statusElement) {
    statusElement.innerHTML = data.status;

    const validatorVersionElement = document.getElementById(`result-validator-${data.guid}`);
    validatorVersionElement.innerHTML = data.validator_version;

    const errorMessageElement = document.getElementById(`result-error-${data.guid}`);
    errorMessageElement.innerHTML = data.error_message
  }
});
