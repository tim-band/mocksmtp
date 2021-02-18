FROM python:alpine
ENV PYTHONUNBUFFERED=1
COPY mocksmtp.py .
CMD ["python", "mocksmtp.py"]
