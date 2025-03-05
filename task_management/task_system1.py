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
    
    # Get the task id
    task_id = c.lastrowid
    
    # Log the task creation in the history
    change_type = "created"
    change_description = "Task '{}' was created.".format(title)  # Updated for Python 2.7
    change_timestamp = created_at
    c.execute("INSERT INTO task_history (task_id, change_type, change_description, change_timestamp) VALUES (?, ?, ?, ?)",
              (task_id, change_type, change_description, change_timestamp))

    conn.commit()
    conn.close()
    print("Task added successfully.")

# Edit an existing task
def edit_task(task_id, new_title, new_description):
    conn = create_connection()
    c = conn.cursor()
    
    updated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Get current task details
    c.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    task = c.fetchone()
    
    if task is None:
        print("Task not found.")
        return
    
    # Update the task
    c.execute("UPDATE tasks SET title=?, description=?, updated_at=? WHERE id=?",
              (new_title, new_description, updated_at, task_id))
    
    # Log the task edit in the history
    change_type = "updated"
    change_description = "Task '{}' was updated to '{}'.".format(task[1], new_title)  # Updated for Python 2.7
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
    
    # Get current task details
    c.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    task = c.fetchone()
    
    if task is None:
        print("Task not found.")
        return
    
    # Mark the task as completed
    c.execute("UPDATE tasks SET status='completed', updated_at=? WHERE id=?",
              (completed_at, task_id))
    
    # Log the task completion in the history
    change_type = "completed"
    change_description = "Task '{}' was marked as completed.".format(task[1])  # Updated for Python 2.7
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

    # Get task details to ensure it exists
    c.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    task = c.fetchone()
    
    if task is None:
        print("Task not found.")
        return
    
    # Delete the task from the tasks table
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    
    # Delete associated history from the task_history table
    c.execute("DELETE FROM task_history WHERE task_id=?", (task_id,))

    conn.commit()
    conn.close()
    print("Task deleted successfully.")

# Reset the system (delete all tasks and history)
def reset_system():
    conn = create_connection()
    c = conn.cursor()

    # Delete all tasks and history
    c.execute("DELETE FROM tasks")
    c.execute("DELETE FROM task_history")

    conn.commit()
    conn.close()
    print("System reset successfully. All tasks and history have been deleted.")

# View all tasks
def view_tasks():
    conn = create_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM tasks")
    tasks = c.fetchall()
    
    if not tasks:
        print("No tasks found.")
    else:
        for task in tasks:
            print("ID: {} | Title: {} | Status: {} | Created At: {} | Updated At: {}".format(task[0], task[1], task[3], task[4], task[5]))
    
    conn.close()

# View task history
def view_task_history(task_id):
    conn = create_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM task_history WHERE task_id=?", (task_id,))
    histories = c.fetchall()
    
    if not histories:
        print("No history found for this task.")
    else:
        for history in histories:
            print("Change Type: {} | Description: {} | Timestamp: {}".format(history[2], history[3], history[4]))
    
    conn.close()

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
        print("7. Reset System")  # Added option to reset system
        print("8. Exit")

        choice = raw_input("Choose a command: ")
        
        if choice == "1":
            title = raw_input("Enter task title: ")
            description = raw_input("Enter task description: ")
            add_task(title, description)
        
        elif choice == "2":
            task_id = int(raw_input("Enter task ID to edit: "))
            new_title = raw_input("Enter new task title: ")
            new_description = raw_input("Enter new task description: ")
            edit_task(task_id, new_title, new_description)
        
        elif choice == "3":
            task_id = int(raw_input("Enter task ID to mark as completed: "))
            complete_task(task_id)
        
        elif choice == "4":
            view_tasks()
        
        elif choice == "5":
            task_id = int(raw_input("Enter task ID to view history: "))
            view_task_history(task_id)
        
        elif choice == "6":
            task_id = int(raw_input("Enter task ID to delete: "))
            delete_task(task_id)  # Handle task deletion
        
        elif choice == "7":
            confirm = raw_input("Are you sure you want to reset the system? This will delete all tasks and history (yes/no): ").lower()
            if confirm == 'yes':
                reset_system()  # Reset the system
            else:
                print("System reset canceled.")
        
        elif choice == "8":
            print("Exiting the Task Management Tool.")
            sys.exit(0)
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

