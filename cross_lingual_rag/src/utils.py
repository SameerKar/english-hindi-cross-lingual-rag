"""
Utility functions for configuration, path resolution, random seeds, and latency profiling.
"""

import os
import sys
import time
import json
import random
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
import numpy as np

def get_project_root() -> Path:
    """
    Locates the cross_lingual_rag project root directory reliably.
    """
    # Check if current directory or immediate subdirectory contains config.yaml
    cwd = Path.cwd()
    if (cwd / "config.yaml").exists():
        return cwd
    if (cwd / "cross_lingual_rag" / "config.yaml").exists():
        return cwd / "cross_lingual_rag"
    
    # Check relative to this file's location
    file_root = Path(__file__).resolve().parent.parent
    if (file_root / "config.yaml").exists():
        return file_root
        
    return cwd

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Loads and parses config.yaml, resolving path references to absolute paths.
    Automatically loads environment variables from .env if present.
    """
    root = get_project_root()
    
    # Auto-load .env from project root or parent workspace
    try:
        import dotenv
        if (root / ".env").exists():
            dotenv.load_dotenv(root / ".env")
        if (root.parent / ".env").exists():
            dotenv.load_dotenv(root.parent / ".env")
        dotenv.load_dotenv()
    except Exception:
        pass

    if config_path is None:
        target_path = root / "config.yaml"
    else:
        target_path = Path(config_path)
        if not target_path.is_absolute():
            target_path = root / target_path
            
    if not target_path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {target_path}")

    with open(target_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Resolve paths section relative to project root
    if "paths" in config:
        for key, rel_path in config["paths"].items():
            abs_p = (root / rel_path).resolve()
            config["paths"][key] = str(abs_p)

    return config

def set_seed(seed: int = 42) -> None:
    """
    Enforces deterministic execution for reproducibility.
    """
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

class TimeTracker:
    """
    Context manager and stopwatch for measuring execution latencies in milliseconds.
    """
    def __init__(self):
        self.start_time: float = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000.0

    def start(self):
        self.start_time = time.perf_counter()

    def stop(self) -> float:
        self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000.0
        return self.elapsed_ms

def ensure_directory(path_str: str) -> Path:
    """
    Ensures a directory exists, creating parents if necessary.
    """
    p = Path(path_str)
    p.mkdir(parents=True, exist_ok=True)
    return p
