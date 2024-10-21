import psycopg2

# Function to connect to PostgreSQL and run a query with parameters
def run_query_with_params(param1, param2):
    # PostgreSQL connection parameters (replace with your credentials)
    host = "localhost"       # Update with your host
    database = "your_db"      # Update with your database name
    user = "your_user"        # Update with your username
    password = "your_password"  # Update with your password

    # SQL query with placeholders for parameters
    query = """
    SELECT column1, column2, column3
    FROM your_table
    WHERE column1 = %s AND column2 = %s
    """

    try:
        # Establish connection to the PostgreSQL database
        conn = psycopg2.connect(
            host=host, 
            database=database, 
            user=user, 
            password=password
        )

        # Create a cursor object to execute the query
        cursor = conn.cursor()

        # Execute the query, passing parameters as a tuple
        cursor.execute(query, (param1, param2))

        # Fetch all results
        results = cursor.fetchall()

        # Print the results
        for row in results:
            print(row)

        # Close the cursor and connection
        cursor.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if conn:
            conn.close()

# Example usage:
param1_value = input("Enter value for param1: ")  # Get the first parameter from the user
param2_value = input("Enter value for param2: ")  # Get the second parameter from the user

run_query_with_params(param1_value, param2_value)
