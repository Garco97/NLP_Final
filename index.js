const { ipcRenderer } = require('electron')
var input = document.getElementById("suggestions");
var textarea = document.getElementById("textarea");
input.addEventListener("keyup",sendInfo);
var add = false;
ipcRenderer.on('ping' , function(event , args){ 
    if (args == "THE END"){
        add = false;
    }
    if (add){
        if(textarea.value){
            textarea.value += "\n"+args;
        }else{
            textarea.value += args;
        }
    }else{
        if(args == "unigram"){
            textarea.value = "";
            add = true;
        }
    }
    
});
function sendInfo(e){
    if(input.value != ""){
        ipcRenderer.send('asynchronous-message', input.value);
    }else{
        textarea.value = "";
    }
}
