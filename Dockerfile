FROM python:3.8
LABEL maiainer "Test <test@tet@test.com>"
RUN apt-get update
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD python app.py
ENV FLASK_ENV="docker"
EXPOSE 5000

#COPY ./requirements.txt /app/requirements.txt

#WORKDIR /app

#RUN pip install -r requirements.txt

#ENTRYPOINT [ "python" ]

#CMD [ "app.py" ]
