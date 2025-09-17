# Import libraries 
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv


url = "https://en.wikipedia.org/wiki/List_of_best-selling_singles"

# Send a GET request to the URL
response = requests.get(url)

# Parse the content of the page with BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all tables on the page
tables = soup.find_all('table', class_="wikitable")

# Initialize a list to store dataframes
dfs = []

# New column names
new_columns = ["Artist", "Single", "Year Released", "Sales"]

# Function to clean the sales column
def clean_sales(sales):
    return re.sub(r'[^\d.]', '', str(sales))

# Loop through the first five tables
for i, table in enumerate(tables[:5]):
    # Use pandas to read the HTML table into a DataFrame
    df = pd.read_html(str(table))[0]

    # Remove the "Source" column for each table
    if "Source" in df.columns:
        df = df.drop(columns=["Source"])

    # Replace column names
    df.columns = new_columns

    # Clean the Sales column
    df["Sales"] = df["Sales"].apply(clean_sales)

    dfs.append(df)

# Append the first five tables
combined_df = pd.concat(dfs, ignore_index=True)

# Load environment variables from .env file
load_dotenv()

# Get database credentials from environment variables
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Create a connection string
connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Create a SQLAlchemy engine
engine = create_engine(connection_string)

# Save the dataframe to the database
combined_df.to_sql('Best Selling Singles', engine, if_exists='replace', index=False)

print("Data successfully saved to the database.")