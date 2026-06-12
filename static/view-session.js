
document.addEventListener("DOMContentLoaded", () =>
{ const republishBtn = document.getElementById("republish-btn");
  republishBtn.addEventListener("click", republish); } );

  function republish() {
    fetch("/get-ci-metadata", { method: "GET", headers: { "Accept": "application/json" } })
      .then(response => response.json())
      .then(data => console.log(data))
      .catch(error => console.error(error));

     const republishBtn = document.getElementById("republish-btn");
    republishBtn.setAttribute("disabled", "");

    // fetch("/republish", {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json"
    //   }
    // })
    // .then(response => {
    //   if (response.ok) {
    //     alert("Collection instruments republished successfully.");
    //     location.reload();
    //   } else {
    //     alert("Failed to republish collection instruments.");
    //   }
    // })
    // .catch(error => {
    //   console.error("Error:", error);
    //   alert("An error occurred while republishing collection instruments.");
    // });
  }
