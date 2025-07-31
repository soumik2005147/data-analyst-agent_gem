import duckdb

# Initialize DuckDB in-process connection
con = duckdb.connect()

# Install and load the required extensions
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL parquet; LOAD parquet;")

# Set the AWS region (you can also add credentials if needed)
con.execute("SET s3_region='ap-south-1';")

# If you need to use credentials (for private buckets), uncomment and set these:
# con.execute("SET s3_access_key_id='YOUR_ACCESS_KEY';")
# con.execute("SET s3_secret_access_key='YOUR_SECRET_KEY';")

# Query the Parquet files from S3
result = con.execute("""
    SELECT COUNT(*)
    FROM read_parquet('s3://indian-high-court-judgments/metadata/parquet/year=*/court=*/bench=*/metadata.parquet?s3_region=ap-south-1');
""").fetchall()

print("Total rows:", result[0][0])
