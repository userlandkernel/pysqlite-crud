import sys
import os
import sqlite3

# Function to get table schema
def get_table_schema(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

# Function to generate a class with CRUD methods for a table
def generate_class_for_table(table_name, schema):
    class_definition = f"class Crud_{table_name.capitalize()}:\n"
    class_definition += "    def __init__(self, connection):\n"
    class_definition += "        self.conn = connection\n"
    class_definition += "        self.cursor = self.conn.cursor()\n\n"
    
    # Create method
    columns = ', '.join([col[1] for col in schema])
    placeholders = ', '.join(['?'] * len(schema))
    class_definition += f"    def create(self, {columns}):\n"
    class_definition += f"        self.cursor.execute(\"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})\", ({columns}))\n"
    class_definition += "        self.conn.commit()\n\n"
    
    # Read method
    class_definition += f"    def read(self, **filters):\n"
    class_definition += "        query = f\"SELECT * FROM "+f"{table_name}"+f"\"\n"
    class_definition += "        if filters:\n"
    class_definition += "            filter_clauses = [f\"{column} = ?\" for column in filters]\n"
    class_definition += "            query += \" WHERE \" + \" AND \".join(filter_clauses)\n"
    class_definition += "        self.cursor.execute(query, tuple(filters.values()))\n"
    class_definition += "        return self.cursor.fetchall()\n\n"
    
    # Update method
    class_definition += "    def update(self, id, **updates):\n"
    class_definition += "        update_clauses = ', '.join([f\"{column} = ?\" for column in updates])\n"
    class_definition += "        values = list(updates.values()) + [id]\n"
    class_definition += "        self.cursor.execute(f\"UPDATE "+f"{table_name}"+f" SET"+ "{update_clauses}"+f"WHERE {schema[0][1]} = ?\", values)\n"
    class_definition += "        self.conn.commit()\n\n"

    # Delete method
    class_definition += f"    def delete(self, id):\n"
    class_definition += f"        self.cursor.execute(\"DELETE FROM {table_name} WHERE {schema[0][1]} = ?\", (id,))\n"
    class_definition += "        self.conn.commit()\n\n"
    
    return class_definition

# Main function to generate CRUD classes for all tables in the database
def generate_crud_classes(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Get the list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Start writing to the output file
    with open(os.path.splitext(os.path.basename(db_name))[0]+"_crud.py", 'w') as file:
        file.write("import sqlite3\n\n")
        file.write(f"conn = sqlite3.connect('{db_name}')\n\n")
        
        # Generate a class for each table
        for table in tables:
            table_name = table[0]
            schema = get_table_schema(cursor, table_name)
            class_definition = generate_class_for_table(table_name, schema)
            file.write(class_definition)
        
        # Close the connection
        file.write("conn.close()\n")
        
    print(f"CRUD classes for all tables in '{db_name}' have been written to 'crud_classes.py'.")

# Call the function with the database name
if __name__ == "__main__":
  if len(sys.argv) <= 1:
    print("Please specify the database name like so: ./crud-generate.py [example.sqlite3]")
    exit(1)
  # Generate the classes
  generate_crud_classes(sys.argv[1])
