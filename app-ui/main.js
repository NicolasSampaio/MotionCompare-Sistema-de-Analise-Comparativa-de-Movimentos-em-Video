const { app, BrowserWindow } = require("electron");
const path = require("path");

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  // Em desenvolvimento, carrega o servidor de desenvolvimento do Angular
  if (process.env.NODE_ENV === "development") {
    win.loadURL("http://localhost:4200");
    win.webContents.openDevTools();
  } else {
    // Em produção, carrega o arquivo index.html compilado
    win.loadFile(path.join(__dirname, "dist/dance-comparison-app/index.html"));
  }
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
