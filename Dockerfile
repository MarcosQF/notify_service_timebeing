# Imagem base oficial do Python
FROM python:3.11-slim

# Variáveis de ambiente para o Poetry
ENV POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y curl && apt-get clean

# Instala o Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Cria diretório de trabalho
WORKDIR /app

# Copia os arquivos de projeto
COPY pyproject.toml poetry.lock ./
COPY . .

# Instala dependências com Poetry
RUN poetry install --no-root --no-interaction --no-ansi

# Comando padrão para rodar o consumidor
CMD ["python", "main.py"]
