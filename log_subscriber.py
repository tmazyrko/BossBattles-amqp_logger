#!/usr/bin/env python3

import pika
from dotenv import dotenv_values
import signal
import sys
import argparse


def signal_handler(signal, frame):  # Graceful CTRL+C handler
    print(" [*] Exiting log_subscriber.py")
    f.write("### STOPPED LOGGING ###\n")
    f.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

parser = argparse.ArgumentParser(description="Subscribes to log messages sent via RabbitMQ.")
parser.add_argument('output', action="store", type=argparse.FileType('a'), help="Name of output file")
args = parser.parse_args()
f = args.output

cfg = dotenv_values(".env")

# Sets up RabbitMQ connection
connection = pika.BlockingConnection(pika.URLParameters(cfg['AMQP_URL']))

channel = connection.channel()
channel.exchange_declare(exchange='logs', exchange_type="fanout", durable=True)

queue = channel.queue_declare(queue='', exclusive=True)
queue_name = queue.method.queue

channel.queue_bind(exchange='logs', queue=queue_name)

print(' [*] Waiting for logs. Press CTRL+C to exit.')
f.write("### STARTED LOGGING ###\n")


def callback(ch, method, properties, body):
    msg = body.decode("utf-8")
    f.write(msg + '\n')
    print(msg)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
