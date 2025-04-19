FROM python:3.9.21

WORKDIR /code

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

# We want 8001 to be expose outside
EXPOSE 8001 

# My Mac only support MPS (GPU like device in MacBook)
# MPS is not working well with multi-process, hence more than 1 workers can cause alot of crashes
# Hence, it is more optimised to only use more threads for handling the file downloading.
CMD ["gunicorn", "asr_api:app", "--workers", "1", "--threads", "2", "--bind", "0.0.0.0:8001"]