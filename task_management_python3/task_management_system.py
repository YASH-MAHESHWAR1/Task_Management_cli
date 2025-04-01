import sqlite3
import sys
import datetime

# Create a connection to the SQLite database
def create_connection():
    return sqlite3.connect("tasks.db")

# Create necessary tables
def create_tables():
    conn = create_connection()
    c = conn.cursor()

    # Create tasks table
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT
                )''')

    # Create task history table
    c.execute('''CREATE TABLE IF NOT EXISTS task_history (
                    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    change_type TEXT NOT NULL,
                    change_description TEXT,
                    change_timestamp TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                )''')

    conn.commit()
    conn.close()

# Add a new task
def add_task(title, description):
    conn = create_connection()
    c = conn.cursor()
    created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "incomplete"

    c.execute("INSERT INTO tasks (title, description, status, created_at) VALUES (?, ?, ?, ?)",
              (title, description, status, created_at))

    task_id = c.lastrowid
    change_type = "created"
    change_description = f"Task '{title}' was created."
    change_timestamp = created_at
    c.execute("INSERT INTO task_history (task_id, change_type, change_description, change_timestamp) VALUES (?, ?, ?, ?)",
              (task_id, change_type, change_description, change_timestamp))

    conn.commit()
    conn.close()
    print("Task added successfully.")

# Print table with proper orientation
def print_table(data, headers):
    if not data:
        print("No records found.")
        return
    
    col_widths = [max(len(str(item)) for item in col) for col in zip(headers, *data)]
    format_str = " | ".join(["{:<" + str(width) + "}" for width in col_widths])
    
    print(format_str.format(*headers))
    print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))
    
    for row in data:
        print(format_str.format(*row))

# View all tasks
def view_tasks():
    conn = create_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM tasks")
    tasks = c.fetchall()

    headers = ["ID", "Title", "Description", "Status", "Created At", "Updated At"]
    print_table(tasks, headers)

    conn.close()

# View task history
def view_task_history(task_id):
    conn = create_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM task_history WHERE task_id=?", (task_id,))
    histories = c.fetchall()

    headers = ["History ID", "Task ID", "Change Type", "Description", "Change Timestamp"]
    print_table(histories, headers)

    conn.close()

# Edit an existing task
def edit_task(task_id, new_title, new_description):
    conn = create_connection()
    c = conn.cursor()
    updated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    c.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    task = c.fetchone()

    if task is None:
        print("Task not found.")
        return

    c.execute("UPDATE tasks SET title=?, description=?, updated_at=? WHERE id=?",
              (new_title, new_description, updated_at, task_id))

    change_type = "updated"
    change_description = f"Task '{task[1]}' was updated to '{new_title}'."
    change_timestamp = updated_at
    c.execute("INSERT INTO task_history (task_id, change_type, change_description, change_timestamp) VALUES (?, ?, ?, ?)",
              (task_id, change_type, change_description, change_timestamp))

    conn.commit()
    conn.close()
    print("Task updated successfully.")

# Mark a task as completed
def complete_task(task_id):
    conn = create_connection()
    c = conn.cursor()

    completed_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute("SELECT title FROM tasks WHERE id=?", (task_id,))
    task = c.fetchone()

    if not task:
        print("Task not found.")
        return
    
    c.execute("UPDATE tasks SET status='completed', updated_at=? WHERE id=?", (completed_at, task_id))
    
    change_type = "completed"
    change_description = f"Task '{task[0]}' was marked as completed."
    change_timestamp = completed_at
    c.execute("INSERT INTO task_history (task_id, change_type, change_description, change_timestamp) VALUES (?, ?, ?, ?)",
              (task_id, change_type, change_description, change_timestamp))
    
    conn.commit()
    conn.close()
    print("Task marked as completed.")

# Delete a task
def delete_task(task_id):
    conn = create_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    task = c.fetchone()

    if task is None:
        print("Task not found.")
        return

    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    c.execute("DELETE FROM task_history WHERE task_id=?", (task_id,))

    conn.commit()
    conn.close()
    print("Task deleted successfully.")

# Main function to run the CLI
def main():
    create_tables()

    print("Welcome to the Task Management Tool!")

    while True:
        print("\nCommands:")
        print("1. Add Task")
        print("2. Edit Task")
        print("3. Complete Task")
        print("4. View Tasks")
        print("5. View Task History")
        print("6. Delete Task")
        print("7. Exit")

        choice = input("Choose a command: ")

        if choice == "1":
            title = input("Enter task title: ")
            description = input("Enter task description: ")
            add_task(title, description)
        elif choice == "2":
            task_id = int(input("Enter task ID to edit: "))
            new_title = input("Enter new task title: ")
            new_description = input("Enter new task description: ")
            edit_task(task_id, new_title, new_description)
        elif choice == "3":
            task_id = int(input("Enter task ID to mark as completed: "))
            complete_task(task_id)
        elif choice == "4":
            view_tasks()
        elif choice == "5":
            task_id = int(input("Enter task ID to view history: "))
            view_task_history(task_id)
        elif choice == "6":
            task_id = int(input("Enter task ID to delete: "))
            delete_task(task_id)
        elif choice == "7":
            print("Exiting the Task Management Tool.")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
