window.ipcRenderer = require("electron").ipcRenderer;

const effectslib = require("effectslib");
const { contextBridge } = require('electron');
contextBridge.exposeInMainWorld("effectslib", effectslib);
