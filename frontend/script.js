const BASE_URL = "http://127.0.0.1:8000";

async function uploadPDF(){

    const fileInput = document.getElementById("pdfFile");

    if(fileInput.files.length===0){

        alert("Choose a PDF first.");
        return;

    }

    const formData = new FormData();

    formData.append("file",fileInput.files[0]);

    const response = await fetch(BASE_URL+"/upload",{

        method:"POST",
        body:formData

    });

    const data = await response.json();

    document.getElementById("uploadStatus").innerText=data.message;

}

async function askQuestion(){

    const question=document.getElementById("question").value;

    const response=await fetch(BASE_URL+"/ask",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({

            question:question

        })

    });

    const data=await response.json();

    document.getElementById("answer").innerText=

        data.answer+"\n\nSource : "+data.source;

}