import json
import pytest
from pathlib import Path
from src.report.exporters.json import JSONExporter
from src.report.exporters.validators import JSONValidator

@pytest.fixture
def sample_data():
    return {
        "results": [
            {"id": 1, "name": "Teste 1", "score": 0.95},
            {"id": 2, "name": "Teste 2", "score": 0.85}
        ],
        "metadata": {
            "version": "1.0",
            "timestamp": "2024-03-19"
        }
    }

@pytest.fixture
def temp_json_file(tmp_path):
    return tmp_path / "test_output.json"

def test_json_exporter_export(sample_data, temp_json_file):
    # Arrange
    exporter = JSONExporter(sample_data)
    
    # Act
    exporter.export(str(temp_json_file))
    
    # Assert
    assert temp_json_file.exists()
    with open(temp_json_file, 'r', encoding='utf-8') as f:
        exported_data = json.load(f)
    assert exported_data == sample_data

def test_json_exporter_invalid_data():
    # Arrange
    invalid_data = {"results": [{"id": 1, "name": "Teste 1", "score": float('inf')}]}
    
    # Act & Assert
    with pytest.raises(ValueError):
        JSONExporter(invalid_data)

def test_json_validator(temp_json_file, sample_data):
    # Arrange
    with open(temp_json_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f)
    
    # Act
    validated_data = JSONValidator.validate(str(temp_json_file))
    
    # Assert
    assert validated_data == sample_data

def test_json_validator_invalid_file():
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        JSONValidator.validate("nonexistent.json")

def test_json_validator_invalid_json(temp_json_file):
    # Arrange
    with open(temp_json_file, 'w', encoding='utf-8') as f:
        f.write("invalid json content")
    
    # Act & Assert
    with pytest.raises(json.JSONDecodeError):
        JSONValidator.validate(str(temp_json_file)) 
