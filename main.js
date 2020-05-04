const {app, BrowserWindow} = require('electron');
const electron = require('electron');
const debug = require('electron-debug');
const unhandled = require('electron-unhandled');
const contextMenu = require('electron-context-menu');
const { ipcMain } = require('electron')
const nano = require('nanomsg');
const exec = require('child_process').exec;
var pair;
function connection(){
    var addr = 'ipc://127.0.0.1:54272'
    pair = nano.socket('pair');
    pair.bind(addr);
    pair.setEncoding('utf8');
    pair.on('data',function(buf){
        if(buf == "Training" || buf == "Training finished"){
            console.log(buf);
        }else{
            win.webContents.send('ping',buf)
        }
    });
}

function createWindow () {
    debug();
    unhandled();
    contextMenu();
    win = new BrowserWindow({width: 1366, height: 768, webPreferences:{nodeIntegration: true}});  
    win.loadFile('index.html'); 
    screen = electron.screen;
}
ipcMain.on('asynchronous-message', (event, arg) => {
    pair.send(arg)
});
connection() 
exec('python3 prenotebook.py', (error, stdout, stderr) =>{
      console.log(stdout);
}); 

app.on('ready', createWindow)