import csv
import pytest
from pathlib import Path
from src.report.exporters.csv import CSVExporter
from src.report.exporters.validators import CSVValidator

@pytest.fixture
def sample_data():
    return {
        "results": [
            {"id": 1, "name": "Teste 1", "score": 0.95},
            {"id": 2, "name": "Teste 2", "score": 0.85}
        ]
    }

@pytest.fixture
def simple_data():
    return {
        "id": 1,
        "name": "Teste 1",
        "score": 0.95
    }

@pytest.fixture
def temp_csv_file(tmp_path):
    return tmp_path / "test_output.csv"

def test_csv_exporter_export_results(sample_data, temp_csv_file):
    # Arrange
    exporter = CSVExporter(sample_data)
    
    # Act
    exporter.export(str(temp_csv_file))
    
    # Assert
    assert temp_csv_file.exists()
    with open(temp_csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        exported_data = list(reader)
    assert len(exported_data) == 2
    assert exported_data[0]["id"] == "1"
    assert exported_data[0]["name"] == "Teste 1"
    assert exported_data[0]["score"] == "0.95"

def test_csv_exporter_export_simple(simple_data, temp_csv_file):
    # Arrange
    exporter = CSVExporter(simple_data)
    
    # Act
    exporter.export(str(temp_csv_file))
    
    # Assert
    assert temp_csv_file.exists()
    with open(temp_csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        exported_data = list(reader)
    assert len(exported_data) == 1
    assert exported_data[0]["id"] == "1"
    assert exported_data[0]["name"] == "Teste 1"
    assert exported_data[0]["score"] == "0.95"

def test_csv_exporter_invalid_data():
    # Arrange
    invalid_data = {"results": "não é uma lista"}
    
    # Act & Assert
    with pytest.raises(ValueError):
        CSVExporter(invalid_data)

def test_csv_validator(temp_csv_file, sample_data):
    # Arrange
    with open(temp_csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "score"])
        writer.writeheader()
        writer.writerows(sample_data["results"])
    
    # Act
    validated_data = CSVValidator.validate(str(temp_csv_file))
    
    # Assert
    assert len(validated_data) == 2
    assert validated_data[0]["id"] == "1"
    assert validated_data[0]["name"] == "Teste 1"
    assert validated_data[0]["score"] == "0.95"

def test_csv_validator_invalid_file():
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        CSVValidator.validate("nonexistent.csv")

def test_csv_validator_invalid_csv(temp_csv_file):
    # Arrange
    with open(temp_csv_file, 'w', encoding='utf-8') as f:
        f.write("invalid,csv,content\n")
        f.write("1,2,3,4\n")  # Número incorreto de colunas
    
    # Act & Assert
    with pytest.raises(csv.Error):
        CSVValidator.validate(str(temp_csv_file)) 
