import os
import sys
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model_env = os.getenv("GEMINI_MODEL")

print(f"API_KEY_PRESENT: {'PRESENTE' if api_key else 'AUSENTE'}")
print(f"MODELO_CONFIGURADO: {model_env}")
print(f"SDK: google-genai module loaded")

client = genai.Client(api_key=api_key)

print("\n--- MODELOS DISPONIVEIS ---")
available_models = []
try:
    for m in client.models.list():
        methods = getattr(m, 'supported_generation_methods', [])
        if "generateContent" in methods:
            available_models.append(m.name)
            print(f"Nome: {m.name}, Capacidades: {methods}")
except Exception as e:
    print(f"Erro ao listar modelos: {e}")

print("\n--- RESULTADOS DOS TESTES ---")
test_targets = []
if model_env: test_targets.append(model_env)
test_targets.extend(["gemini-3.5-flash", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"])
test_targets = list(dict.fromkeys(test_targets))

for target in test_targets:
    print(f"\nTestando: {target}")
    try:
        response = client.models.generate_content(
            model=target,
            contents="responda 'ok'"
        )
        print(f"[{target}] HTTP/status: 200 -> resultado: {response.text.strip()}")
    except Exception as e:
        print(f"[{target}] HTTP/status: ERROR -> resultado: {e}")
