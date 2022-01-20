const PaModule = require('pa-module');
const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('paModule', PaModule);
