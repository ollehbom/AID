import pandas as pd

def process_data(df):
    # Some processing logic
    print("Starting data processing...")
    df['new_col'] = df['old_col'] * 2
    print("Processing data") # Fixed line 25: Added missing parenthesis
    return df

if __name__ == "__main__":
    data = {'old_col': [1, 2, 3]}
    df = pd.DataFrame(data)
    processed_df = process_data(df)
    print("Data processing complete.")
