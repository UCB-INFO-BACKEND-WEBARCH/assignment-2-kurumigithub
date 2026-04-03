import time
import logging

logging.basicConfig(level=logging.INFO)

def send_reminder(task_title):
    # simulate sending a reminder
    time.sleep(5)
    logging.info(f"Reminder: Task '{task_title}' is due soon!")