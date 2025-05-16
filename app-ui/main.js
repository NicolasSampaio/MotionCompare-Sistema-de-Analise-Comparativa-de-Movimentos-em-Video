const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 720,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  // Carrega a aplicação Angular
  mainWindow.loadURL("http://localhost:4200");

  // Abre o DevTools em desenvolvimento
  if (process.env.NODE_ENV === "development") {
    mainWindow.webContents.openDevTools();
  }
}

function startPythonProcess() {
  // Inicia o processo Python
  pythonProcess = spawn("python", ["../main_core.py"], {
    stdio: ["pipe", "pipe", "pipe"],
  });

  // Manipula erros do processo Python
  pythonProcess.stderr.on("data", (data) => {
    console.error(`Erro do Python: ${data}`);
  });

  // Manipula a saída do processo Python
  pythonProcess.stdout.on("data", (data) => {
    try {
      const response = JSON.parse(data.toString());
      mainWindow.webContents.send("python-response", response);
    } catch (error) {
      console.error("Erro ao processar resposta do Python:", error);
    }
  });
}

// Inicia a aplicação quando o Electron estiver pronto
app.whenReady().then(() => {
  createWindow();
  startPythonProcess();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Encerra a aplicação quando todas as janelas forem fechadas
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    if (pythonProcess) {
      pythonProcess.kill();
    }
    app.quit();
  }
});

// Manipula mensagens do renderer process
ipcMain.on("process-frame", (event, frameData) => {
  if (pythonProcess && pythonProcess.stdin.writable) {
    pythonProcess.stdin.write(JSON.stringify(frameData) + "\n");
  }
});
