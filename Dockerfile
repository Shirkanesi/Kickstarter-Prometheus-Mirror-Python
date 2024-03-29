FROM python:3.9.1
# Install and update dependencies
RUN pip install --upgrade pip
RUN pip install requests
# Copy script
COPY kickstarter-mirror.py /home/app/main.py

# Run script
ENTRYPOINT ["python", "/home/app/main.py"]
