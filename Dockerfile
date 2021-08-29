FROM python:3.9.1
# Copy script
COPY kickstarter-mirror.py /home/app/main.py
# Install and update dependencies
RUN pip install --upgrade pip
RUN pip install requests

# Run script
ENTRYPOINT ["python", "/home/app/main.py"]