# Import required libraries
import pymysql
import google.generativeai as genai
import streamlit as st

# Streamlit title and description
st.title("SQL Query Generator")
st.write("Enter natural language questions to generate and execute SQL queries on your MySQL database.")

# Database configuration inputs
db_host = st.text_input("Enter database host:", "localhost")
db_user = st.text_input("Enter database username:", "root")
db_password = st.text_input("Enter database password:", type="password")
db_name = st.text_input("Enter database name:", "sales")

# Google Generative AI key configuration
genai.configure(api_key='AIzaSyC_o_ejuFBIsEgpW2vJ_8uzGYmARbAdaQA')

# Set up the model configuration
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# Prompt setup for SQL generation .
input_prompt = st.text_area("Enter your custom SQL prompt:", 
                            "You are an expert in converting English questions to SQL code!")

# Connect to the database
def connect_to_database():
    try:
        db_connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        st.write("Database connected successfully.")
        return db_connection, db_connection.cursor()
    except pymysql.MySQLError as err:
        st.error(f"Database connection error: {err}")
        return None, None

# Function to generate SQL query using AI model
@st.cache_data  # Cache the SQL generation only
def generate_sql_query(question, input_prompt):
    prompt_parts = [input_prompt, question]
    response = model.generate_content(prompt_parts)
    return response.text.strip()

# Streamlit input for the question
question = st.text_input("Enter your question:")
if st.button("Generate and Execute SQL Query"):
    if question:
        # Generate SQL query
        sql_query = generate_sql_query(question, input_prompt)
        
        # Clean up the generated SQL query
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        st.write("Generated SQL Query:")
        st.code(sql_query, language='sql')

        # Connect to the database and execute the query
        db_connection, cursor = connect_to_database()
        if db_connection and cursor:
            try:
                cursor.execute(sql_query)   
                results = cursor.fetchall()
                if results:
                    # Display results in a table
                    st.write("Query Results:")
                    st.table(results)
                else:
                    st.write("No results found.")
            except pymysql.MySQLError as err:
                st.error(f"Query Execution Error: {err}")
            finally:
                # Close the connection after each query execution
                cursor.close()
                db_connection.close()
        else:
            st.error("Could not connect to the database.")
    else:
        st.warning("Please enter a question.")
