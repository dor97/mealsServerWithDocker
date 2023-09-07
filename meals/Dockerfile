FROM python:alpine3.10

# 
WORKDIR /app

# 
COPY meals.py .

# 
# 
RUN pip install  flask
RUN pip install requests
RUN pip install pymongo


# 
COPY . /app 

EXPOSE 5001

# 
CMD ["python", "meals.py"]

