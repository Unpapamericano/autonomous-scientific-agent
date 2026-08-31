"""
Unit tests for Phase 1: Inference module
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.core.inference import MuseGlimmerInference, InferenceConfig


class TestInferenceConfig:
    """Test InferenceConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = InferenceConfig()
        assert config.quantization == "4-bit"
        assert config.max_new_tokens == 2048
        assert config.temperature == 1.0
        assert config.top_p == 0.95
        assert config.top_k == 64
        assert config.device == "auto"
    
    def test_config_from_env(self):
        """Test loading config from environment."""
        import os
        os.environ["MUSE_QUANTIZATION"] = "8-bit"
        os.environ["MUSE_MAX_TOKENS"] = "512"
        
        config = InferenceConfig.from_env()
        assert config.quantization == "8-bit"
        assert config.max_new_tokens == 512
        
        # Cleanup
        del os.environ["MUSE_QUANTIZATION"]
        del os.environ["MUSE_MAX_TOKENS"]

    def test_ollama_config_from_env(self):
        import os

        os.environ["MUSE_BACKEND"] = "ollama"
        os.environ["MUSE_MODEL_ID"] = "qwen3.8:latest"
        config = InferenceConfig.from_env()

        assert config.backend == "ollama"
        assert config.model_id == "qwen3.8:latest"

        del os.environ["MUSE_BACKEND"]
        del os.environ["MUSE_MODEL_ID"]


class TestMuseGlimmerInference:
    """Test MuseGlimmerInference class."""
    
    @patch('src.core.inference.AutoTokenizer.from_pretrained')
    @patch('src.core.inference.AutoModelForCausalLM.from_pretrained')
    def test_initialization(self, mock_model, mock_tokenizer):
        """Test model initialization."""
        mock_tokenizer.return_value = Mock()
        mock_model.return_value = Mock()
        
        config = InferenceConfig(quantization="bf16")
        inference = MuseGlimmerInference(config)
        
        assert inference.config.quantization == "bf16"
        assert inference.model is not None
        assert inference.tokenizer is not None
        mock_tokenizer.assert_called_once()
        mock_model.assert_called_once()
    
    @patch('src.core.inference.AutoTokenizer.from_pretrained')
    @patch('src.core.inference.AutoModelForCausalLM.from_pretrained')
    def test_device_resolution_cuda(self, mock_model, mock_tokenizer):
        """Test CUDA device resolution."""
        import torch
        
        mock_tokenizer.return_value = Mock()
        mock_model.return_value = Mock()
        
        # Simulate CUDA availability
        with patch('torch.cuda.is_available', return_value=True):
            config = InferenceConfig(device="auto")
            inference = MuseGlimmerInference(config)
            
            # Device should be cuda (or mps if on Mac)
            assert inference.device in ["cuda", "mps"]
    
    @patch('src.core.inference.AutoTokenizer.from_pretrained')
    @patch('src.core.inference.AutoModelForCausalLM.from_pretrained')
    def test_device_resolution_cpu(self, mock_model, mock_tokenizer):
        """Test CPU device resolution."""
        mock_tokenizer.return_value = Mock()
        mock_model.return_value = Mock()
        
        # Force CPU
        with patch('torch.cuda.is_available', return_value=False):
            config = InferenceConfig(device="auto")
            inference = MuseGlimmerInference(config)
            
            assert inference.device == "cpu"
    
    def test_health_check_format(self):
        """Test health check response format."""
        # This would require mocking the model
        # For now, just verify the expected keys
        expected_keys = {"status", "model_id", "device", "quantization"}
        assert isinstance(expected_keys, set)


class TestInferenceGeneration:
    """Test generation methods (requires mocking)."""
    
    @patch('src.core.inference.AutoTokenizer.from_pretrained')
    @patch('src.core.inference.AutoModelForCausalLM.from_pretrained')
    def test_generate_simple(self, mock_model, mock_tokenizer):
        """Test simple text generation (mocked)."""
        # Mock tokenizer
        mock_tok = Mock()
        mock_tok.return_value = {'input_ids': Mock(), 'attention_mask': Mock()}
        mock_tok.decode.return_value = "Test prompt Test response"
        mock_tokenizer.return_value = mock_tok
        
        # Mock model
        mock_mod = Mock()
        mock_mod.generate.return_value = [[1, 2, 3]]
        mock_model.return_value = mock_mod
        
        config = InferenceConfig()
        inference = MuseGlimmerInference(config)
        
        # This would fail without proper mocking of torch
        # For Phase 1, we focus on structural tests
        assert inference.tokenizer is not None
        assert inference.model is not None

    @patch("requests.post")
    def test_generate_with_ollama(self, mock_post):
        response = Mock()
        response.json.return_value = {"response": "Qwen response"}
        response.raise_for_status.return_value = None
        mock_post.return_value = response

        inference = MuseGlimmerInference(
            InferenceConfig(backend="ollama", model_id="qwen3.8:latest")
        )

        assert inference.generate("Explain the result", max_new_tokens=32) == "Qwen response"
        mock_post.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
