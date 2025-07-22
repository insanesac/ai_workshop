"""
Production LLM Client for StudyBuddy System
Extracted from Notebook 2 for reusability across applications
"""

import os
import sys
import logging
import warnings
from typing import Dict, List, Any, Optional, Mapping
from datetime import datetime

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Configure logging
logger = logging.getLogger(__name__)

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    from langchain.llms.base import LLM
except ImportError as e:
    logger.error(f"Required dependencies not installed: {e}")
    raise


class ProductionLLMClient:
    """
    Production-grade LLM client for multi-agent systems.
    Optimized for Qwen2.5-14B with proper error handling and monitoring.
    
    This is the exact same implementation from Notebook 2, extracted for reusability.
    """
    
    def __init__(self, model=None, tokenizer=None, model_name=None):
        """
        Initialize production LLM client.
        Can be initialized with pre-loaded components or load fresh.
        
        Args:
            model: Pre-loaded Hugging Face model (optional)
            tokenizer: Pre-loaded tokenizer (optional)
            model_name: Model identifier for logging (optional)
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if model is not None and tokenizer is not None:
            # Use pre-loaded components
            self.model = model
            self.tokenizer = tokenizer
            self.model_name = model_name or "qwen2.5-14b-instruct"
            self.logger.info(f"🤖 Using pre-loaded model: {self.model_name}")
        else:
            # Load fresh components
            self.model_name = "unsloth/Qwen2.5-14B-Instruct-bnb-4bit"
            self._load_model()
        
        # Production metrics
        self.request_count = 0
        self.total_tokens_generated = 0
        
        self.logger.info(f"🤖 Production LLM Client initialized")
        self.logger.info(f"📝 Model: {self.model_name}")
        self.logger.info(f"🎯 Ready for agent integration")
    
    def _load_model(self):
        """Load model and tokenizer fresh"""
        self.logger.info(f"🔄 Loading model: {self.model_name}")
        
        try:
            # Check hardware capabilities
            if torch.cuda.is_available():
                device = "cuda"
                self.logger.info(f"🔧 Using GPU: {torch.cuda.get_device_name(0)}")
            else:
                device = "cpu"
                self.logger.warning("⚠️ No GPU detected, using CPU")
            
            # Load tokenizer
            self.logger.info("📝 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            
            # Ensure we have a pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.logger.info("🤖 Loading model...")
            if device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    device_map="auto",
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    device_map=None,
                    trust_remote_code=True
                ).to(device)
            
            self.model.eval()
            self.logger.info("✅ Model loaded successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def generate_response(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7, 
                         system_message: Optional[str] = None) -> str:
        """
        Generate high-quality response for agent use.
        
        Args:
            prompt: Input prompt for the LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            system_message: Optional system message to set context/personality
            
        Returns:
            Generated response from Qwen2.5-14B
        """
        self.request_count += 1
        
        try:
            return self._generate_qwen_response(prompt, max_tokens, temperature, system_message)
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again."
    
    def _generate_qwen_response(self, prompt: str, max_tokens: int, temperature: float, 
                               system_message: Optional[str] = None) -> str:
        """Generate response using Qwen2.5-14B-Instruct"""
        
        # Qwen uses standard chat format
        default_system = "You are a helpful AI assistant for learning and productivity."
        system_content = system_message if system_message else default_system
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]
        
        # Apply chat template
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Tokenize
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(self.model.device)
        
        # Generate with production-optimized parameters
        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=min(max_tokens, 400),
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
                use_cache=True
            )
        
        # Decode only the new tokens
        input_length = inputs.input_ids.shape[1]
        new_tokens = outputs[0][input_length:]
        response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        # Clean up response
        response = response.strip()
        
        # Update metrics
        self.total_tokens_generated += len(new_tokens)
        
        # Quality validation
        if len(response) < 5:
            return "I'd be happy to help you with that! Could you provide more specific details?"
        
        return response
    
    def get_stats(self) -> Dict[str, Any]:
        """Get production metrics for monitoring"""
        return {
            "model": self.model_name,
            "requests_processed": self.request_count,
            "total_tokens_generated": self.total_tokens_generated,
            "average_tokens_per_request": self.total_tokens_generated / max(self.request_count, 1)
        }


class QwenLangChainLLM(LLM):
    """
    LangChain-compatible wrapper for our Qwen2.5-14B model.
    This allows seamless integration with LangChain agents and tools.
    
    Extracted from Notebook 3 for reusability.
    """
    
    def __init__(self, production_llm_client: ProductionLLMClient):
        super().__init__()
        self.client = production_llm_client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    @property
    def _llm_type(self) -> str:
        return "qwen2.5-14b-instruct"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> str:
        """
        Execute the LLM call for LangChain agents.
        
        Args:
            prompt: The prompt to send to the model
            stop: Stop sequences (not used in our implementation)
            run_manager: LangChain run manager
            **kwargs: Additional arguments
            
        Returns:
            Generated response from Qwen2.5-14B
        """
        # Extract parameters with defaults
        max_tokens = kwargs.get('max_tokens', 200)
        temperature = kwargs.get('temperature', 0.7)
        
        try:
            response = self.client.generate_response(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again."
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "model_name": self.client.model_name,
            "model_type": "qwen2.5-14b-instruct-bnb-4bit"
        }


def ensure_production_llm() -> ProductionLLMClient:
    """
    Production pattern: Lazy initialization with caching.
    
    This function ensures a production LLM client is available,
    either by reusing an existing one or creating a fresh instance.
    
    This is exactly what we need for cross-notebook compatibility!
    """
    global _cached_llm_client
    
    # Check if we already have a cached client
    if '_cached_llm_client' in globals() and _cached_llm_client is not None:
        logger.info("✅ Using cached LLM client")
        return _cached_llm_client
    
    # Check if we can reuse components from notebook environment
    try:
        # Try to access notebook-level variables
        import __main__
        if hasattr(__main__, 'llm') and hasattr(__main__, 'model') and hasattr(__main__, 'tokenizer'):
            logger.info("✅ Reusing LLM components from notebook environment")
            _cached_llm_client = ProductionLLMClient(
                model=__main__.model,
                tokenizer=__main__.tokenizer,
                model_name=getattr(__main__, 'model_name', 'qwen2.5-14b-instruct')
            )
            return _cached_llm_client
    except:
        pass  # Notebook components not available
    
    # Create fresh instance
    logger.info("🔄 Creating fresh LLM client")
    _cached_llm_client = ProductionLLMClient()
    return _cached_llm_client


# Global cache
_cached_llm_client = None
