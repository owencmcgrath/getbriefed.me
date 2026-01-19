from caldav import DAVClient
from datetime import datetime


def get_reminders(username, password):
    client = DAVClient(
        url="https://contacts.icloud.com/", 
        username=username,
        password=password
    )

    principal = client.principal()
    reminders = []

    for cal in principal.calendars():
        if 'reminders' in cal.name.lower() or 'tasks' in cal.name.lower():
            print(f"Found reminders list: {cal.name}")
            try:
                todos = cal.search(todo=True, include_completed=False)
                print(f"Todos: {todos}")

                for todo in todos:
                    todo_data = todo.vobject_instance.vtodo
                    reminders.append({
                        'title': str(todo_data.summary.value),
                        'due': ''
                    })
            except Exception as e:
                print(f"Error: {e}")

    return reminders  
