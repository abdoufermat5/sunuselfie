FROM continuumio/miniconda3
LABEL authors="abdoufermat"
MAINTAINER AbdouFermat

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
RUN pip install git+https://github.com/vladkens/twscrape.git
RUN conda install -c conda-forge --file /app/requirements.txt

# Copy project
COPY . /app/

EXPOSE 8501

# Run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

