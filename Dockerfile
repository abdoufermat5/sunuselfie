FROM python:3.10-bookworm
LABEL authors="asadiakhou"

# Set environment variables
# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1

# Install system dependencies libgl1-mesa-glx
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Set work directory
WORKDIR /app

# Install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir \
    --trusted-host pypi.python.org --trusted-host pypi.org\
    --trusted-host=files.pythonhosted.org

# Copy project
COPY . /app/

EXPOSE 8501

# Run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

