from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from typing import Dict, Any, Optional
import sys
from .base import BaseVisualizer
from .plots import PlotManager

class VisualizerCLI(BaseVisualizer):
    """Interface CLI para visualização interativa dos resultados de análise."""
    
    def __init__(self, report_data: Dict[str, Any]):
        """
        Inicializa o visualizador CLI.
        
        Args:
            report_data: Dicionário contendo os dados do relatório
        """
        super().__init__(report_data)
        self.console = Console()
        self.plot_manager = PlotManager()
        self.running = True
        
    def start(self) -> None:
        """Inicia a interface CLI interativa."""
        self.console.clear()
        self.console.print(Panel.fit(
            "[bold blue]Visualizador de Análise de Dança[/bold blue]\n"
            "Use os comandos para navegar pelos resultados",
            title="Bem-vindo"
        ))
        
        while self.running:
            self._show_menu()
            command = Prompt.ask("\nDigite um comando", choices=self._get_commands())
            self._handle_command(command)
            
    def _show_menu(self) -> None:
        """Mostra o menu principal de comandos."""
        table = Table(title="Comandos Disponíveis")
        table.add_column("Comando", style="cyan")
        table.add_column("Descrição", style="green")
        
        commands = {
            "s": "Mostrar gráfico de similaridade",
            "f": "Navegar para um frame específico",
            "n": "Próximo frame",
            "p": "Frame anterior",
            "d": "Mostrar detalhes do frame atual",
            "q": "Sair"
        }
        
        for cmd, desc in commands.items():
            table.add_row(cmd, desc)
            
        self.console.print(table)
        
    def _get_commands(self) -> list:
        """Retorna lista de comandos disponíveis."""
        return ["s", "f", "n", "p", "d", "q"]
        
    def _handle_command(self, command: str) -> None:
        """
        Processa o comando do usuário.
        
        Args:
            command: Comando digitado pelo usuário
        """
        if command == "s":
            self.plot_similarity()
        elif command == "f":
            self._navigate_to_frame()
        elif command == "n":
            self._next_frame()
        elif command == "p":
            self._previous_frame()
        elif command == "d":
            self.show_frame_details(self.current_frame)
        elif command == "q":
            self.running = False
            self.console.print("[yellow]Saindo do visualizador...[/yellow]")
        else:
            raise ValueError(f"Comando inválido: {command}")
            
    def plot_similarity(self) -> None:
        """Plota o gráfico de similaridade entre as sequências."""
        similarity_data = self.get_similarity_data()
        
        if 'matrix' in similarity_data:
            self.plot_manager.plot_similarity_heatmap(similarity_data['matrix'])
        if 'scores' in similarity_data:
            self.plot_manager.plot_similarity_line(similarity_data['scores'])
            
        self.plot_manager.show()
        
    def plot_frame_comparison(self, frame_idx: int) -> None:
        """
        Plota a comparação detalhada de um frame específico.
        
        Args:
            frame_idx: Índice do frame a ser visualizado
        """
        frame_data = self.get_frame_data(frame_idx)
        self.plot_manager.plot_frame_comparison(
            frame_data,
            title=f"Comparação do Frame {frame_idx}"
        )
        self.plot_manager.show()
        
    def show_frame_details(self, frame_idx: int) -> None:
        """
        Mostra detalhes específicos de um frame.
        
        Args:
            frame_idx: Índice do frame a ser visualizado
        """
        frame_data = self.get_frame_data(frame_idx)
        
        table = Table(title=f"Detalhes do Frame {frame_idx}")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")
        
        for metric, value in frame_data.get('metrics', {}).items():
            table.add_row(metric, f"{value:.4f}")
            
        self.console.print(table)
        self.plot_frame_comparison(frame_idx)
        
    def _navigate_to_frame(self) -> None:
        """Navega para um frame específico."""
        try:
            frame_idx = int(Prompt.ask(
                f"Digite o número do frame (0-{self.total_frames-1})"
            ))
            if 0 <= frame_idx < self.total_frames:
                self.current_frame = frame_idx
                self.show_frame_details(frame_idx)
            else:
                self.console.print("[red]Número de frame inválido![/red]")
        except ValueError:
            self.console.print("[red]Por favor, digite um número válido![/red]")
            
    def _next_frame(self) -> None:
        """Navega para o próximo frame."""
        if self.current_frame < self.total_frames - 1:
            self.current_frame += 1
            self.show_frame_details(self.current_frame)
        else:
            self.console.print("[yellow]Já está no último frame![/yellow]")
            
    def _previous_frame(self) -> None:
        """Navega para o frame anterior."""
        if self.current_frame > 0:
            self.current_frame -= 1
            self.show_frame_details(self.current_frame)
        else:
            self.console.print("[yellow]Já está no primeiro frame![/yellow]") 
