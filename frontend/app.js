const fileInput = document.getElementById("fileInput");
const previewImage = document.getElementById("previewImage");
const scanBtn = document.getElementById("scanBtn");
const resultBox = document.getElementById("resultBox");
const errorBox = document.getElementById("errorBox");
const spinner = document.getElementById("spinner");

const API_URL = window.API_URL || "http://localhost:8000/scan";

let selectedFile = null;

function resetState() {
  resultBox.textContent = "{}";
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

fileInput.addEventListener("change", (event) => {
  resetState();
  const file = event.target.files[0];
  if (!file) {
    previewImage.style.display = "none";
    scanBtn.disabled = true;
    selectedFile = null;
    return;
  }

  if (!file.type.startsWith("image/")) {
    errorBox.textContent = "Please select a PNG or JPEG image.";
    errorBox.classList.remove("hidden");
    scanBtn.disabled = true;
    previewImage.style.display = "none";
    selectedFile = null;
    return;
  }

  selectedFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImage.src = e.target.result;
    previewImage.style.display = "block";
  };
  reader.readAsDataURL(file);
  scanBtn.disabled = false;
});

scanBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    return;
  }
  resetState();

  spinner.classList.remove("hidden");
  scanBtn.disabled = true;

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Scan failed.");
    }

    resultBox.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.classList.remove("hidden");
  } finally {
    spinner.classList.add("hidden");
    scanBtn.disabled = false;
  }
});

