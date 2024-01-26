document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json()) // Parse the response as JSON
      .then((data) => {
        console.log(data); // Log the result to the console

        // Make sure 'result' is the correct key based on your Flask app response
        const processedText = data.result || "";

        document.getElementById("processedText").innerHTML = processedText;
      })
      .catch((error) => console.error("Error:", error));
  });
});
