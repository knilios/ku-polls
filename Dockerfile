FROM python:3-alpine

WORKDIR /app/polls
COPY . .

# Install dependencies in Docker container
RUN pip install -r requirements.txt

RUN python -c "from django.core.management.utils import get_random_secret_key; f = open('.env', 'w'); f.write('SECRET_KEY=django-insecure-'+get_random_secret_key()+'\n'); f.close()"
ENV DEBUG=False
ENV ALLOWED_HOSTS=*
ENV TIME_ZONE=Asia/Bangkok

RUN chmod +x ./entrypoint.sh

EXPOSE 9000
# Run application
CMD [ "./entrypoint.sh" ]