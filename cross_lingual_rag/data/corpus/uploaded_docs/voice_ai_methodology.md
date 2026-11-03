# Research Methodology on Voice AI

--- PAGE 1 ---
The voice agent platform utilizes WebSockets to stream PCM audio bidirectionally between the user client and the cloud inference pipeline.
The speech-to-text pipeline processes acoustic packets in 20ms chunks using an optimized deep neural network.

--- PAGE 2 ---
The dialogue manager maintains conversation state in a distributed cache with sub-10ms round-trip latency.
Text-to-speech generation synthesizes phonemes with emotional prosody and pitch matching.
