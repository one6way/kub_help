from mage_ai.data_preparation.decorators import data_loader, transformer, data_exporter
import pandas as pd
import numpy as np

@data_loader
def load_data(*args, **kwargs):
    """
    Generate sample data for testing
    """
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    data = {
        'date': dates,
        'sales': np.random.normal(1000, 100, len(dates)),
        'customers': np.random.randint(50, 200, len(dates))
    }
    return pd.DataFrame(data)

@transformer
def transform_data(data, *args, **kwargs):
    """
    Transform the data
    """
    # Add some calculations
    data['average_purchase'] = data['sales'] / data['customers']
    data['day_of_week'] = data['date'].dt.day_name()
    
    # Round numeric columns
    data['sales'] = data['sales'].round(2)
    data['average_purchase'] = data['average_purchase'].round(2)
    
    return data

@data_exporter
def export_data(data, *args, **kwargs):
    """
    Export the transformed data
    """
    # In a real scenario, you might want to save to a database or file
    # For this test, we'll just print some statistics
    print("\nData Statistics:")
    print("================")
    print(f"Total Records: {len(data)}")
    print("\nSales Summary:")
    print(data['sales'].describe())
    print("\nAverage Purchase by Day:")
    print(data.groupby('day_of_week')['average_purchase'].mean().round(2))
    
    return data
