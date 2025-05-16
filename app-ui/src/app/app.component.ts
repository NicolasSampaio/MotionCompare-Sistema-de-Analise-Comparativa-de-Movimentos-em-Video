import { Component, OnInit, OnDestroy } from '@angular/core';
declare const ipcRenderer: any;

@Component({
  selector: 'app-root',
  template: `
    <div class="container">
      <h1>Sistema de Análise Comparativa de Movimentos de Dança</h1>
      <div class="video-container">
        <video #videoElement [srcObject]="stream" autoplay></video>
        <canvas #canvasElement></canvas>
      </div>
      <div class="status">
        <p>Status: {{ status }}</p>
      </div>
    </div>
  `,
  styles: [
    `
      .container {
        padding: 20px;
        text-align: center;
      }
      .video-container {
        margin: 20px auto;
        max-width: 1280px;
        position: relative;
      }
      video,
      canvas {
        width: 100%;
        height: auto;
      }
      canvas {
        position: absolute;
        top: 0;
        left: 0;
      }
      .status {
        margin-top: 20px;
        font-size: 1.2em;
      }
    `,
  ],
})
export class AppComponent implements OnInit, OnDestroy {
  stream: MediaStream | null = null;
  status: string = 'Inicializando...';
  private videoElement: HTMLVideoElement | null = null;
  private canvasElement: HTMLCanvasElement | null = null;
  private animationFrameId: number | null = null;

  async ngOnInit() {
    try {
      // Inicializa a câmera
      this.stream = await navigator.mediaDevices.getUserMedia({ video: true });
      this.status = 'Câmera inicializada';

      // Configura os elementos de vídeo e canvas
      this.videoElement = document.querySelector('video');
      this.canvasElement = document.querySelector('canvas');

      if (this.videoElement && this.canvasElement) {
        this.canvasElement.width = this.videoElement.videoWidth;
        this.canvasElement.height = this.videoElement.videoHeight;

        // Inicia o loop de processamento
        this.processFrame();
      }
    } catch (error) {
      this.status = `Erro ao inicializar câmera: ${error}`;
    }
  }

  ngOnDestroy() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
    }
  }

  private processFrame() {
    if (!this.videoElement || !this.canvasElement) return;

    const context = this.canvasElement.getContext('2d');
    if (!context) return;

    // Desenha o frame atual
    context.drawImage(this.videoElement, 0, 0);

    // Obtém os dados do frame
    const imageData = context.getImageData(
      0,
      0,
      this.canvasElement.width,
      this.canvasElement.height
    );

    // Envia o frame para o processo Python
    ipcRenderer.send('process-frame', {
      frame: Array.from(imageData.data),
    });

    // Agenda o próximo frame
    this.animationFrameId = requestAnimationFrame(() => this.processFrame());
  }
}
