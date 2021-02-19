FROM python:alpine
ENV PYTHONUNBUFFERED=1
RUN pip install aiosmtpd
COPY mocksmtp.py .
CMD ["python", "mocksmtp.py"]
