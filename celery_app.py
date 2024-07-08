# from celery import Celery
# import os

# # Use the CLOUDAMQP_URL environment variable if available, otherwise default to local RabbitMQ
# rabbitmq_url = os.getenv('CLOUDAMQP_URL', 'amqp://localhost')

# celery = Celery(__name__, broker=rabbitmq_url, backend='rpc://')

# import main_summary


from celery import Celery
import os

# Use the REDIS_URL environment variable if available, otherwise default to local Redis
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

celery = Celery('tasks', broker=redis_url, backend=redis_url)

import main_summary