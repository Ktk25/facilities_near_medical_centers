FROM python:3.8

RUN mkdir -p /home/app

COPY . /home/app

RUN pip install -r /home/app/requirements.txt

CMD ["streamlit", "run", "/home/app/Facility_Features_App.py"]


