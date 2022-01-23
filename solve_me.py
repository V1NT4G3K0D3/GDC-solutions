from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def push(self, priority, temp):
        while True:
            if priority in self.current_items: # check if new priority has a key in dict
                todo_string = temp # holds previously overwritten string / newly added string
                temp = self.current_items[priority] # holds string that is going to be overwritten
                self.current_items[priority] = todo_string # overwrites the string with the prev key's string
                priority+=1 
            else:
                break
        self.current_items[priority] = temp
            
    def add(self, args):
        priority, todo_string = int(args[0]), args[1]
        self.push(priority, todo_string)  
        self.write_current()   
        print(f"Added task: \"{todo_string}\" with priority {str(priority)}")
                
    def done(self, args):
        priority = int(args[0])
        if priority in self.current_items:
            todo_string = self.current_items[priority]
            self.completed_items.append(todo_string)
            del self.current_items[priority]
            self.write_current() 
            self.write_completed()
            print("Marked item as done.") 
        else:
            print(f"Error: no incomplete item with priority {str(priority)} exists.")  

    def delete(self, args):
        priority = int(args[0])
        if priority in self.current_items:
            del self.current_items[priority]
            self.write_current()   
            print("Deleted item with priority " + str(priority)) 
        else:
            print("Error: item with priority " + str(priority) + " does not exist. Nothing deleted.")  
        
    def ls(self):
        for index, (key, value) in enumerate(self.current_items.items()):
            print(str(index+1) + ". " + value + " [" + str(key) + "]")

    def report(self):
        print("Pending : " + str(len(self.current_items)))
        self.ls()
        print("\nCompleted : " + str(len(self.completed_items)))
        for index, item in enumerate(self.completed_items):
            print(str(index+1) + ". " + item.strip('\n'))

    def render_pending_tasks(self):
        self.read_current()
        content = f"""
            <h1>Incomplete tasks: </h1>
            <ol>
        """
        for index, (key, value) in enumerate(self.current_items.items()):
            content += f"<li>{value} [{str(key)}]</li>"
        content += f"</ol>"
        
        return content

    def render_completed_tasks(self):
        self.read_completed()
        content = f"""
            <h1>Completed tasks: </h1>
            <ol>
        """
        for index, item in enumerate(self.completed_items):
            content += f"<li>{item}</li>"
        content += f"</ol>"
        return content
        
class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
