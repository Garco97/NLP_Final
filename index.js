const { ipcRenderer } = require('electron')
var input = document.getElementById("suggestions");
var textarea = document.getElementById("textarea");
input.addEventListener("keyup",sendInfo);
var add = false;
ipcRenderer.on('ping' , function(event , args){ 
    inp = input.value.split(" ")
    inp.pop()
    
    argu = args.split(" ")


    if (inp[inp.length-1] == argu[0]){
        argu.shift();
    }
    if (inp[inp.length-1] == ""){
        inp.pop();
    }

    if (args == "THE END"){
        add = false;
    }
    if (add){
        output = inp.toString().replace(","," ");
        argum = argu.toString().replace(","," ")
        for(var i = 0; i<7;i++){
            output = output.toString().replace(","," ");
            argum = argum.toString().replace(","," ")

        }
        if(textarea.value){
            if(output){
                textarea.value += "\n"+output +" "+argum;
            }else{
                textarea.value += "\n"+argum;
                
            }
        }else{
            if(output){
                
                textarea.value += output+" "+argum;
            }else{
                textarea.value += argum;
                
            }
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
