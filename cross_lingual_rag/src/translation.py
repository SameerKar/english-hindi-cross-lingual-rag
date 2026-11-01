"""
Translation layer for System C (Translation-Mediated RAG).
Translates queries and responses between Hindi and English while recording exact latencies and errors.
Includes multi-provider failover: GoogleTranslator -> MyMemoryTranslator -> Semantic Fallback.
Works across ANY domain (Computer Science, Voice AI, Medicine, Law, Engineering, General).
"""

import time
import re
from typing import Tuple, Optional, Dict, Any

class TranslationService:
    """
    Handles translation between Hindi and English with latency tracking, multi-engine retry,
    and zero rate-limiting fallback mechanisms.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        trans_cfg = config.get("translation", {})
        self.provider = trans_cfg.get("provider", "deep-translator")
        self.source_lang = trans_cfg.get("source_lang", "hi")
        self.target_lang = trans_cfg.get("target_lang", "en")

    def translate_hi_to_en(self, text: str) -> Tuple[str, float, Optional[str]]:
        """
        Translates Hindi input text to English.
        Returns: (translated_text, latency_ms, error_message)
        """
        return self._execute_translation(text, src="hi", tgt="en")

    def translate_en_to_hi(self, text: str) -> Tuple[str, float, Optional[str]]:
        """
        Translates English text to Hindi.
        Returns: (translated_text, latency_ms, error_message)
        """
        return self._execute_translation(text, src="en", tgt="hi")

    def _execute_translation(self, text: str, src: str, tgt: str) -> Tuple[str, float, Optional[str]]:
        if not text or not text.strip():
            return "", 0.0, None

        start_time = time.perf_counter()
        error_msg = None
        translated = None

        clean_text = text.strip()

        # Engine 1: Google Translator
        try:
            from deep_translator import GoogleTranslator
            g_trans = GoogleTranslator(source=src, target=tgt)
            res = g_trans.translate(clean_text)
            if res and res.strip() and not (src == "hi" and tgt == "en" and self._is_mostly_devanagari(res)):
                translated = res.strip()
        except Exception as e:
            error_msg = f"GoogleTranslator notice: {str(e)}"

        # Engine 2: MyMemory Translator (Extremely reliable fallback when Google 429s)
        if not translated:
            try:
                from deep_translator import MyMemoryTranslator
                # MyMemory uses locale tags (hi-IN, en-GB / en-US)
                src_tag = "hi-IN" if src == "hi" else "en-GB"
                tgt_tag = "en-GB" if tgt == "en" else "hi-IN"
                mm_trans = MyMemoryTranslator(source=src_tag, target=tgt_tag)
                res = mm_trans.translate(clean_text)
                if res and res.strip():
                    translated = res.strip()
                    error_msg = None
            except Exception as e:
                error_msg = f"MyMemory fallback notice: {str(e)}"

        # Engine 3: Semantic Fallback for academic phrases if both MT web engines are offline
        if not translated:
            translated = self._semantic_fallback(clean_text, src, tgt)

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return translated or clean_text, latency_ms, error_msg

    def _is_mostly_devanagari(self, text: str) -> bool:
        """Returns True if text is still predominantly Devanagari script."""
        deva_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        return deva_count > (len(text) * 0.4)

    def _semantic_fallback(self, text: str, src: str, tgt: str) -> str:
        """Fallback phrase mapper for offline resilience."""
        vocab = {
            "आर्किटेक्चर": "architecture",
            "वॉयस एजेंट": "voice agent",
            "प्लेटफॉर्म": "platform",
            "सिस्टम": "system",
            "एल्गोरिदम": "algorithm",
            "डेटाबेस": "database",
            "नेटवर्क": "network",
            "प्रोटोकॉल": "protocol",
            "क्या है": "what is",
            "क्या हैं": "what are",
            "कैसे काम करता है": "how does it work",
            "का": "of", "की": "of", "के": "of",
            "में": "in", "पर": "on", "और": "and"
        }
        res = text
        for hi, en in vocab.items():
            res = res.replace(hi, en)
        return res
