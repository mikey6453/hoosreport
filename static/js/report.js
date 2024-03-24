const dropArea = document.querySelector(".drag-image"),
dragText = dropArea.querySelector("h6"),
button = dropArea.querySelector("button"),
input = dropArea.querySelector("input");
let file;

button.onclick = ()=>{
  input.click();
}

input.addEventListener("change", function(){

  file = this.files[0];
  dropArea.classList.add("active");
  viewfile();
});

dropArea.addEventListener("dragover", (event)=>{
  event.preventDefault();
  dropArea.classList.add("active");
  dragText.textContent = "Release to Upload File";
});


dropArea.addEventListener("dragleave", ()=>{
  dropArea.classList.remove("active");
  dragText.textContent = "Drag & Drop to Upload File";
});

dropArea.addEventListener("drop", (event)=>{
  event.preventDefault();

  file = event.dataTransfer.files[0];
  viewfile();
});

function viewfile(){
    let fileType = file.type;
    let validExtensions = ["image/jpeg", "image/jpg", "application/pdf", "text/plain"];
    if(validExtensions.includes(fileType)){
      let formData = new FormData();
      formData.append('file', file);

      document.getElementById('fileName').textContent = file.name;

      fetch('/submitted_report/', {
        method: 'POST',
        body: formData,
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      })
      .then(response => response.json())
      .then(data => console.log(data))
      .catch(error => console.error('Error:', error));
    }else{
      alert("Invalid file type!");
    }
  }

  