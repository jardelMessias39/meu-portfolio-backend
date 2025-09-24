# 🧠 Meu Portfólio Backend

Este é o backend do meu portfólio pessoal, desenvolvido com **FastAPI**, **MongoDB** e integração com a **API da OpenAI**. Ele gerencia sessões de chat, status de sistema e fornece uma base sólida para aplicações modernas em Python.

---

## 🚀 Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com/) — Framework web rápido e moderno
- [MongoDB + Motor](https://motor.readthedocs.io/en/stable/) — Banco de dados NoSQL assíncrono
- [Pydantic](https://docs.pydantic.dev/) — Validação de dados
- [OpenAI API](https://platform.openai.com/docs) — Geração de respostas inteligentes
- [Uvicorn](https://www.uvicorn.org/) — Servidor ASGI leve e rápido

---

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/jardelMessias39/meu-portfolio-backend.git
cd meu-portfolio-backend

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # ou venv\\Scripts\\activate no Windows

# Instale as dependências
pip install -r requirements.txt

# Inicie o servidor
uvicorn server:app --reload
