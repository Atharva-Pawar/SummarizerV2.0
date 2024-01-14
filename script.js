// docs-summery logic

function processText() {
  // Get the value from the textarea
  var inputText = document.getElementById("inputTextarea").value;

  // Process the text (you can replace this with your own logic)
  var processedText = inputText.toUpperCase();

  // Display the processed text
  document.getElementById("processedText").innerText = processedText;
}
