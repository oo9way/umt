function enableSubmitButton() {
  document.getElementById("submit-btn").removeAttribute("disabled");
}

document.getElementById("your-form-id").addEventListener("submit", function () {
  document.getElementById("submit-btn").setAttribute("disabled", "true");
});
