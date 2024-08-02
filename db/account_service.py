
import pyodbc 

database = 'claims-cortex-test-db'
server='tcp:cc-test-develop.database.windows.net';
username = 'azureadmin'
password = 'Austin12.'
port = '1433'


# ENCRYPT defaults to yes starting in ODBC Driver 18. It's good to always specify ENCRYPT=yes on the client side to avoid MITM attacks.
cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+','+port+';DATABASE='+database+';ENCRYPT=yes;TrustServerCertificate=yes;UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

print ('Inserting a new row into table')
#Insert Query
tsql = "INSERT INTO TestSchema.Clients (Username, Password, Address, FullName, Email) VALUES (?,?);"
with cursor.execute(tsql,'Jake','United States'):
    print ('Successfully Inserted!')

# Function to create the Account table if it doesn't exist
def create_account_table():
    create_table_sql = '''
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Account')
    CREATE TABLE dbo.Account (
        Username VARCHAR(255) PRIMARY KEY,
        Password VARCHAR(255),
        Address VARCHAR(255),
        FullName VARCHAR(255),
        Email VARCHAR(255)
    )
    '''
    cursor.execute(create_table_sql)

# Function to update or insert an account
def create_replace_account(account):
    username, password, address, full_name, email = account

    # First, try to update the account
    update_sql = '''
    UPDATE dbo.Account
    SET Password = ?, Address = ?, FullName = ?, Email = ?
    WHERE Username = ?
    '''
    cursor.execute(update_sql, (password, address, full_name, email, username))
    
    # Check if the update was successful (affected rows)
    if cursor.rowcount == 0:
        # If no rows were updated, insert a new account
        insert_sql = '''
        INSERT INTO dbo.Account (Username, Password, Address, FullName, Email)
        VALUES (?, ?, ?, ?, ?)
        '''
        cursor.execute(insert_sql, (username, password, address, full_name, email))
    
    cnxn.commit()
    print('Successfully updated or created the account!')

#Delete Query
# print ('Deleting user Jared')
# tsql = "DELETE FROM TestSchema.Clients WHERE Name = ?"
# with cursor.execute(tsql,'Jared'):
#     print ('Successfully Deleted!')


#Select Query
print ('Reading data from table')
tsql = "SELECT Name, Location FROM TestSchema.Clients;"
with cursor.execute(tsql):
    row = cursor.fetchone()
    while row:
        print (str(row[0]) + " " + str(row[1]))
        row = cursor.fetchone()