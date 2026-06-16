document.addEventListener("DOMContentLoaded", () => {
  const republishBtn = document.getElementById("republish-btn");
  republishBtn.addEventListener("click", republish);
});

for (let i = 0; i < localStorage.length; i++) {
  const key = localStorage.key(i);
  const value = localStorage.getItem(key);
  console.log(key, value);
  const statusCell = document.getElementById(key).cells[5];
  console.log(statusCell.textContent)
  statusCell.textContent = value;
}

for (let i = 0; i < localStorage.length; i++) {
  const key = localStorage.key(i);
  const value = localStorage.getItem(key);
  console.log(key, value);
  const statusCell = document.getElementById(key).cells[5];
  console.log(statusCell.textContent)
  statusCell.textContent = value;

  if (statusCell.textContent === "In Progress") {
    statusCell.textContent = "Not Started";
  }
  else {
    statusCell.textContent = value;
  }
}

function republish() {
  const republishBtn = document.getElementById("republish-btn");
  republishBtn.setAttribute("disabled", "");

  fetch("/get-ci-metadata", { method: "GET", headers: { Accept: "application/json" } })
    .then((response) => response.json())
    .then(async (data) => {
      const items = data["ci_metadata"] ?? [];

      const validItems = items
      .map((item) => ({ guid: item?.cir_id, version: item?.cir_version }))
      .filter(({ guid, version }) => document.getElementById(guid).cells[5].textContent !== "Success");

      // await fetch("/update-session-status", {method: "GET", headers: {Accept: "application/json"}})

      console.log("validated items", validItems)

      if (validItems.length > 0) {
        await Promise.all(
          validItems.map(async ({ guid, version }) => {
            const statusCell = document.getElementById(guid).cells[5];
            statusCell.textContent = "In Progress";
            localStorage.setItem(guid, "In Progress");

            const response = await fetch(
              `http://localhost:8081/republishschema/${guid}/cirversion/${version}`,
              { method: "GET", headers: { Accept: "application/json" } }
            );

            if (!response.ok) {
              statusCell.textContent = "Fail";
              localStorage.setItem(guid, "Fail");
              throw new Error(`Request failed for guid ${guid} version ${version}`);
            }

            const result = await response.json().catch(() => null);
            statusCell.textContent = result?.success ? "Success" : "Fail";
            localStorage.setItem(guid, "Success");

            console.log(`validator-version updated for guid ${guid} and version ${version}`, result);
            return result;
          })
        );
      }
    })
    .catch((error) => console.error(error));
}
