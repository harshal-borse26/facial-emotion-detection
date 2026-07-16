const API_URL = "https://ek65kihf4c.execute-api.eu-north-1.amazonaws.com/prod";
const imageInput = document.getElementById("imageInput");
const previewImage = document.getElementById("previewImage");
const uploadBtn = document.getElementById("uploadBtn");
const fileName = document.getElementById("fileName");
const statusText = document.getElementById("statusText");
const faceCount = document.getElementById("faceCount");
const imageName = document.getElementById("imageName");
const scanTime = document.getElementById("scanTime");
const topEmotion = document.getElementById("topEmotion");
const facesContainer = document.getElementById("facesContainer");
let selectedFile = null;

imageInput.addEventListener("change", (e) => {
  selectedFile = e.target.files[0];

  if (!selectedFile) {
    return;
  }

  fileName.textContent = selectedFile.name;

  previewImage.src = URL.createObjectURL(selectedFile);
});

uploadBtn.addEventListener("click", uploadImage);

async function uploadImage() {
  if (selectedFile == null) {
    alert("Please select an image.");

    return;
  }

  statusText.textContent = "Generating upload URL...";

  try {
    const response = await fetch(
      `${API_URL}/upload?fileName=${selectedFile.name}`,
    );

    const data = await response.json();

    await fetch(
      data.uploadUrl,

      {
        method: "PUT",
        body: selectedFile,
      },
    );

    statusText.textContent = "Image uploaded successfully. Processing...";

    setTimeout(
      loadResults,

      6000,
    );
  } catch (error) {
    console.log(error);

    statusText.textContent = "Upload Failed";
  }
}

async function loadResults() {
  try {
    statusText.textContent = "Loading results...";

    const response = await fetch(`${API_URL}/results`);
    const data = await response.json();

    if (data.length === 0) {
      statusText.textContent = "No results found.";
      return;
    }

    const result = data[0];
    faceCount.textContent = result.faceCount;
    imageName.textContent = result.imageName;
    scanTime.textContent = result.scanTime;

    if (result.faces.length > 0) {
      topEmotion.textContent = result.faces[0].emotion;
    } else {
      topEmotion.textContent = "None";
    }
    facesContainer.innerHTML = "";

    result.faces.forEach((face) => {
      let emotionClass = face.emotion.toLowerCase();

      facesContainer.innerHTML += `

            <div class="face-card">

                <div class="face-header">

                    <h2>

                        Face ${face.faceNumber}

                    </h2>

                    <span class="emotion ${emotionClass}">

                        ${face.emotion}

                    </span>

                </div>

                <div class="face-details">

                    <div class="info">

                        <h4>Age Range</h4>

                        <p>${face.ageRange}</p>

                    </div>

                    <div class="info">

                        <h4>Gender</h4>

                        <p>${face.gender}</p>

                    </div>

                    <div class="info">

                        <h4>Smile</h4>

                        <p>${face.smile ? "Yes 😊" : "No"}</p>

                    </div>

                    <div class="info">

                        <h4>Eyes Open</h4>

                        <p>${face.eyesOpen ? "Open 👀" : "Closed"}</p>

                    </div>

                    <div class="info">

                        <h4>Eyeglasses</h4>

                        <p>${face.eyeglasses ? "Yes 👓" : "No"}</p>

                    </div>

                    <div class="info">

                        <h4>Sunglasses</h4>

                        <p>${face.sunglasses ? "Yes 🕶️" : "No"}</p>

                    </div>

                    <div class="info">

                        <h4>Emotion Confidence</h4>

                        <p>${face.confidence}%</p>

                    </div>

                </div>

            </div>

            `;
    });

    statusText.textContent = "Analysis Completed Successfully";
  } catch (error) {
    console.log(error);

    statusText.textContent = "Unable to fetch results.";
  }
}

window.addEventListener(
  "load",

  loadResults,
);
