import pytest

def test_mediapipe_import():
    """Testa a importação do MediaPipe."""
    import mediapipe as mp
    assert mp is not None

def test_opencv_import():
    """Testa a importação do OpenCV."""
    import cv2
    assert cv2 is not None

def test_numpy_import():
    """Testa a importação do NumPy."""
    import numpy as np
    assert np is not None

if __name__ == "__main__":
    pytest.main([__file__]) 
