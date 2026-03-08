# modelo de ia para cargar en el contenedor

pip install huggingface_hub

huggingface-cli download Qwen/Qwen2.5-1.5B-Instruct-GGUF \
qwen2.5-1.5b-instruct-q4_k_m.gguf \
--local-dir ./model

