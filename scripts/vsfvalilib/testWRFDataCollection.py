from WRFDataCollection import WRFDataCollection

# Path for a specific day's WRF data (e.g., January 13, 2025)
base_path = "/opt/vsfvali/data/wrf/area1/2025/01/12/"
base_path = "/opt/vsfvali/data/wrf/area1/"

# Create a collection for the day's data
wrf_collection = WRFDataCollection(base_path,True)

# Print all loaded datasets (hourly subfolders)
print("Loaded datasets:", wrf_collection.list_data_sets())

# Example: Accessing the dataset for hour "06"
index=0
dataset = wrf_collection.get_data_set(index)

if dataset:
    print("Dataset for index: {} loaded successfully.".format(index))
else:
    print("Dataset for index: {} not found.".format(index))
