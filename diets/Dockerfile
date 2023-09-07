FROM python:alpine3.10

# 
WORKDIR /app

# 
COPY diets.py .

# 
RUN pip install  flask
RUN pip install requests
RUN pip install pymongo

# 
COPY . /app 
EXPOSE 5002

# 
CMD ["python", "diets.py"]

