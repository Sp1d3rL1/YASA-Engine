# test_taint.py

# Simulate a source of tainted data
def user_input():
    return "user-supplied-string"

# Simulate a sink that is vulnerable
def execute_query(query):
    print(f"Executing query: {query}")

# --- Test Scenario ---
raw_input = user_input()
query_string = "SELECT * FROM users WHERE name = '" + raw_input + "'"
execute_query(query_string)