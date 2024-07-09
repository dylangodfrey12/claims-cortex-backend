import pyodbc

# Define the connection string
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=your_server_name;"
    "DATABASE=your_database_name;"
    "UID=your_username;"
    "PWD=your_password"
)

# Establish the connection
try:
    connection = pyodbc.connect(connection_string)
    print("Connection successful!")
    
    # Create a cursor object using the connection
    cursor = connection.cursor()
    
    # Execute a query
    cursor.execute("SELECT @@version;")
    
    # Fetch and print the result
    row = cursor.fetchone()
    while row:
        print(row)
        row = cursor.fetchone()
        
except Exception as e:
    print(f"Error: {e}")

finally:
    # Close the connection
    connection.close()
