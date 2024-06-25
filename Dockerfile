FROM python:3.9.6

COPY . .

RUN pip install -r requirements.txt

CMD python main.py --environment_name "cook_soup" --role server