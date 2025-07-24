import os

REMINDER_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'reminders.txt')

def add_reminder(message: str):
    reminders = get_reminders()
    new_items = [item.strip() for item in message.split(',') if item.strip()]
    reminders.extend(new_items)
    with open(REMINDER_FILE, 'w') as f:
        f.write(', '.join(reminders))

def get_reminders():
    if not os.path.exists(REMINDER_FILE):
        return []
    with open(REMINDER_FILE, 'r') as f:
        content = f.read().strip()
        if not content:
            return []
        return [item.strip() for item in content.split(',')]

def clear_reminders():
    open(REMINDER_FILE, 'w').close()
