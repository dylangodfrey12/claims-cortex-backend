
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

def create_replace_account(account):
    #Update Query
    print ('Updating Location for Nikita')
    tsql = "UPDATE dbo.Account SET Location = ? WHERE Name = ?"
    with cursor.execute(tsql,'Sweden','Nikita'):
        print ('Successfully Updated!')


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