import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from pathlib import Path
import tempfile
import os

from src.gerador_relatorio import ReportGenerator, ReportSection
from src.comparison_results import ComparisonResults, DanceComparison

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para os testes."""
        # Cria resultados de exemplo
        self.results = ComparisonResults(
            video1_path="video1.mp4",
            video2_path="video2.mp4",
            global_score=0.75,
            frame_comparisons=[
                DanceComparison(
                    frame_number=1,
                    similarity_score=0.9
                ),
                DanceComparison(
                    frame_number=2,
                    similarity_score=0.3
                ),
                DanceComparison(
                    frame_number=3,
                    similarity_score=0.8
                )
            ]
        )
        
        self.generator = ReportGenerator(self.results)
        
    def test_init(self):
        """Testa a inicialização do gerador."""
        self.assertEqual(self.generator.results, self.results)
        self.assertEqual(len(self.generator.sections), 0)
        
    def test_validate_results(self):
        """Testa a validação dos resultados."""
        # Teste com resultados válidos
        self.generator._validate_results()  # Não deve lançar exceção
        
        # Teste com resultados inválidos
        invalid_results = Mock(spec=ComparisonResults)
        invalid_results.validate.return_value = False
        
        with self.assertRaises(ValueError):
            ReportGenerator(invalid_results)
            
    def test_generate_global_score(self):
        """Testa a geração do score global."""
        self.generator._generate_global_score()
        
        self.assertEqual(len(self.generator.sections), 1)
        section = self.generator.sections[0]
        
        self.assertEqual(section.title, "Score Global de Similaridade")
        self.assertIn("75.00%", section.content)
        self.assertEqual(section.importance, 3)
        
    def test_generate_frame_analysis(self):
        """Testa a geração da análise por frame."""
        self.generator._generate_frame_analysis()
        
        self.assertEqual(len(self.generator.sections), 1)
        section = self.generator.sections[0]
        
        self.assertEqual(section.title, "Análise por Frame")
        self.assertIn("Análise por Intervalos de Frames", section.content)
        
    def test_group_frames(self):
        """Testa o agrupamento de frames."""
        groups = self.generator._group_frames(group_size=2)
        
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0][0], 1)  # Primeiro frame
        self.assertEqual(groups[0][1], 2)  # Último frame do primeiro grupo
        self.assertAlmostEqual(groups[0][2], 0.6)  # Média do primeiro grupo
        
    def test_generate_agreement_points(self):
        """Testa a geração dos pontos de concordância e divergência."""
        self.generator._generate_agreement_points()
        
        self.assertEqual(len(self.generator.sections), 1)
        section = self.generator.sections[0]
        
        self.assertEqual(section.title, "Pontos de Concordância e Divergência")
        self.assertIn("Pontos Críticos Identificados", section.content)
        
    def test_identify_critical_points(self):
        """Testa a identificação de pontos críticos."""
        points = self.generator._identify_critical_points()
        
        self.assertIn("agreements", points)
        self.assertIn("disagreements", points)
        self.assertEqual(len(points["agreements"]), 1)  # Frame com score 0.9
        self.assertEqual(len(points["disagreements"]), 1)  # Frame com score 0.3
        
    def test_generate_recommendations(self):
        """Testa a geração de recomendações."""
        self.generator._generate_recommendations()
        
        self.assertEqual(len(self.generator.sections), 1)
        section = self.generator.sections[0]
        
        self.assertEqual(section.title, "Recomendações")
        self.assertIn("Recomendações Baseadas na Análise", section.content)
        
    def test_analyze_recommendations(self):
        """Testa a análise para geração de recomendações."""
        recommendations = self.generator._analyze_recommendations()
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
    def test_save(self):
        """Testa o salvamento do relatório."""
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
            
        try:
            # Gera e salva o relatório
            self.generator.generate()
            self.generator.save(temp_path)
            
            # Verifica se o arquivo foi criado
            self.assertTrue(os.path.exists(temp_path))
            
            # Verifica o conteúdo
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.assertIn("RELATÓRIO DE ANÁLISE COMPARATIVA DE DANÇA", content)
            self.assertIn("video1.mp4", content)
            self.assertIn("video2.mp4", content)
            
        finally:
            # Limpa o arquivo temporário
            os.unlink(temp_path)
            
    def test_display(self):
        """Testa a exibição do relatório."""
        with patch('src.gerador_relatorio.console') as mock_console:
            self.generator.generate()
            self.generator.display()
            
            # Verifica se o console.print foi chamado
            mock_console.print.assert_called_once()
            
    def test_format_report(self):
        """Testa a formatação do relatório."""
        self.generator.generate()
        report = self.generator._format_report()
        
        self.assertIn("RELATÓRIO DE ANÁLISE COMPARATIVA DE DANÇA", report)
        self.assertIn("video1.mp4", report)
        self.assertIn("video2.mp4", report)
        
if __name__ == '__main__':
    unittest.main() 
