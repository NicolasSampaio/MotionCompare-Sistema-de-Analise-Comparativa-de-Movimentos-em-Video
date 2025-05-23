from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress
from pathlib import Path

from src.comparison_results import ComparisonResults, DanceComparison

logger = logging.getLogger(__name__)
console = Console()

@dataclass
class ReportSection:
    """Estrutura para representar uma seção do relatório."""
    title: str
    content: str
    importance: int = 1  # 1-3, onde 3 é mais importante

class ReportGenerator:
    """
    Gerador de relatórios de análise comparativa de dança.
    
    Esta classe é responsável por gerar relatórios detalhados a partir dos
    resultados da comparação de movimentos de dança.
    """
    
    def __init__(self, results: ComparisonResults):
        """
        Inicializa o gerador de relatório.
        
        Args:
            results (ComparisonResults): Resultados da comparação
        """
        self.results = results
        self.sections: List[ReportSection] = []
        self._validate_results()
        
    def _validate_results(self) -> None:
        """Valida os resultados da comparação."""
        if not self.results.validate():
            raise ValueError("Resultados da comparação inválidos")
            
    def generate(self) -> 'ReportGenerator':
        """
        Gera o relatório completo.
        
        Returns:
            ReportGenerator: A própria instância para encadeamento
        """
        self._generate_global_score()
        self._generate_frame_analysis()
        self._generate_agreement_points()
        self._generate_recommendations()
        return self
        
    def _generate_global_score(self) -> None:
        """Gera a seção de score global."""
        score = self.results.global_score
        score_text = f"{score:.2%}"
        
        # Determina a cor baseada no score
        if score >= 0.8:
            color = "green"
        elif score >= 0.6:
            color = "yellow"
        else:
            color = "red"
            
        content = f"""
        Score Global de Similaridade: [bold {color}]{score_text}[/]
        
        Este score representa o nível geral de similaridade entre os dois vídeos analisados.
        """
        
        self.sections.append(ReportSection(
            title="Score Global de Similaridade",
            content=content,
            importance=3
        ))
        
    def _generate_frame_analysis(self) -> None:
        """Gera a seção de análise por frame."""
        if not self.results.frame_comparisons:
            content = "Nenhuma análise por frame disponível."
        else:
            # Agrupa frames em intervalos para melhor visualização
            frame_groups = self._group_frames()
            
            content = "Análise por Intervalos de Frames:\n\n"
            for start, end, avg_score in frame_groups:
                content += f"Frames {start}-{end}: {avg_score:.2%}\n"
                
        self.sections.append(ReportSection(
            title="Análise por Frame",
            content=content,
            importance=2
        ))
        
    def _group_frames(self, group_size: int = 10) -> List[tuple]:
        """
        Agrupa os frames em intervalos para melhor visualização.
        
        Args:
            group_size (int): Tamanho do grupo de frames
            
        Returns:
            List[tuple]: Lista de tuplas (início, fim, média)
        """
        frames = self.results.frame_comparisons
        groups = []
        
        for i in range(0, len(frames), group_size):
            group = frames[i:i + group_size]
            start = group[0].frame_number
            end = group[-1].frame_number
            avg_score = sum(f.similarity_score for f in group) / len(group)
            groups.append((start, end, avg_score))
            
        return groups
        
    def _generate_agreement_points(self) -> None:
        """Gera a seção de pontos de concordância e divergência."""
        if not self.results.frame_comparisons:
            content = "Nenhum ponto de concordância/divergência identificado."
        else:
            # Identifica pontos críticos
            critical_points = self._identify_critical_points()
            
            content = "Pontos Críticos Identificados:\n\n"
            
            # Concordâncias
            content += "[bold green]Pontos de Concordância:[/]\n"
            for point in critical_points["agreements"]:
                content += f"- Frame {point['frame']}: {point['description']}\n"
                
            # Divergências
            content += "\n[bold red]Pontos de Divergência:[/]\n"
            for point in critical_points["disagreements"]:
                content += f"- Frame {point['frame']}: {point['description']}\n"
                
        self.sections.append(ReportSection(
            title="Pontos de Concordância e Divergência",
            content=content,
            importance=2
        ))
        
    def _identify_critical_points(self) -> Dict[str, List[Dict]]:
        """
        Identifica pontos críticos de concordância e divergência.
        
        Returns:
            Dict[str, List[Dict]]: Dicionário com pontos de concordância e divergência
        """
        frames = self.results.frame_comparisons
        critical_points = {
            "agreements": [],
            "disagreements": []
        }
        
        for frame in frames:
            if frame.similarity_score >= 0.9:
                critical_points["agreements"].append({
                    "frame": frame.frame_number,
                    "description": "Alta similaridade nos movimentos"
                })
            elif frame.similarity_score <= 0.3:
                critical_points["disagreements"].append({
                    "frame": frame.frame_number,
                    "description": "Diferenças significativas nos movimentos"
                })
                
        return critical_points
        
    def _generate_recommendations(self) -> None:
        """Gera a seção de recomendações."""
        recommendations = self._analyze_recommendations()
        
        content = "Recomendações Baseadas na Análise:\n\n"
        for rec in recommendations:
            content += f"- {rec}\n"
            
        self.sections.append(ReportSection(
            title="Recomendações",
            content=content,
            importance=1
        ))
        
    def _analyze_recommendations(self) -> List[str]:
        """
        Analisa os resultados e gera recomendações.
        
        Returns:
            List[str]: Lista de recomendações
        """
        recommendations = []
        
        # Análise do score global
        if self.results.global_score < 0.6:
            recommendations.append(
                "Os vídeos apresentam diferenças significativas. "
                "Considere revisar os movimentos para maior alinhamento."
            )
        elif self.results.global_score > 0.9:
            recommendations.append(
                "Excelente similaridade entre os vídeos. "
                "Os movimentos estão bem alinhados."
            )
            
        # Análise de frames específicos
        low_scores = [f for f in self.results.frame_comparisons if f.similarity_score < 0.4]
        if low_scores:
            recommendations.append(
                f"Identificados {len(low_scores)} frames com baixa similaridade. "
                "Recomenda-se revisar estes momentos específicos."
            )
            
        return recommendations
        
    def save(self, filepath: str) -> None:
        """
        Salva o relatório em um arquivo.
        
        Args:
            filepath (str): Caminho do arquivo
        """
        path = Path(filepath)
        content = self._format_report()
        
        try:
            path.write_text(content, encoding='utf-8')
            logger.info(f"Relatório salvo em: {filepath}")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")
            raise
            
    def display(self) -> None:
        """Exibe o relatório no terminal."""
        content = self._format_report()
        console.print(Panel(content, title="Relatório de Análise Comparativa"))
        
    def _format_report(self) -> str:
        """
        Formata o relatório completo.
        
        Returns:
            str: Relatório formatado
        """
        # Ordena seções por importância
        sorted_sections = sorted(self.sections, key=lambda x: x.importance, reverse=True)
        
        # Formata o relatório
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE ANÁLISE COMPARATIVA DE DANÇA")
        report.append("=" * 80)
        report.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report.append(f"Vídeo 1: {self.results.video1_path}")
        report.append(f"Vídeo 2: {self.results.video2_path}")
        report.append("=" * 80)
        report.append("")
        
        for section in sorted_sections:
            report.append(f"[bold]{section.title}[/]")
            report.append("-" * len(section.title))
            report.append(section.content)
            report.append("")
            
        return "\n".join(report)
