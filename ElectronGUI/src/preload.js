window.ipcRenderer = require("electron").ipcRenderer;

const PaModule = require('pa-module');
const { contextBridge } = require('electron');
contextBridge.exposeInMainWorld('paModule', PaModule);
