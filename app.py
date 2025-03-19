from sentinelhub import SHConfig, SentinelHubRequest, BBox, CRS, DataCollection, MimeType, bbox_to_dimensions
import numpy as np
from PIL import Image

# 🔥 Step 1: Set up API Configuration
config = SHConfig()
config.sh_client_id = "03720c6c-fd1c-45d8-900b-4fb981d44f53"  # Replace with your client ID
config.sh_client_secret = "7UIVdM75zNY5HNkcEfH5NoPZDvk91OzE"  # Replace with your client secret

if not config.sh_client_id or not config.sh_client_secret:
    print("Please provide Sentinel Hub client ID and secret!")
    exit()

# 🌍 Step 2: Define Bounding Box for Specific Locations
# Chennai: [min_lon, min_lat, max_lon, max_lat]
chennai_bbox = BBox(bbox=[80.20, 12.90, 80.30, 13.10], crs=CRS.WGS84)

# Mumbai: [min_lon, min_lat, max_lon, max_lat]
mumbai_bbox = BBox(bbox=[72.80, 18.90, 72.95, 19.10], crs=CRS.WGS84)

# Select location (Chennai or Mumbai)
location = "chennai"  # Change to "mumbai" for Mumbai
bbox = chennai_bbox if location == "chennai" else mumbai_bbox

# Set resolution and calculate image dimensions
resolution = 60  # 60m per pixel (adjust as needed)
size = bbox_to_dimensions(bbox, resolution)

# Check if the size exceeds the API limit (2500x2500)
if size[0] > 2500 or size[1] > 2500:
    print("Image dimensions exceed the API limit. Adjust the bounding box or resolution.")
    exit()

# 🌍 Step 3: Fetch Real-Time Satellite Image
request = SentinelHubRequest(
    evalscript="""
    function setup() {
        return {
            input: ["B04", "B03", "B02"],
            output: { bands: 3 }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B04, sample.B03, sample.B02];  // RGB bands
    }
    """,
    input_data=[
        {
            "type": "S2L2A",  # Specify the collection type explicitly
            "dataCollection": DataCollection.SENTINEL2_L2A.name,  # Use the serializable format
            "timeInterval": ("2023-03-19", "2023-03-19"),  # Use a valid date range
            "mosaickingOrder": "mostRecent"
        }
    ],
    responses=[
        SentinelHubRequest.output_response("default", MimeType.PNG)
    ],
    bbox=bbox,
    size=size,
    config=config
)

# 🚀 Step 4: Fetch the image
image_data = request.get_data()[0]

# 🌍 Step 5: Save the image as PNG
image = Image.fromarray(np.uint8(image_data))
output_filename = f"{location}_satellite.png"
image.save(output_filename)
print(f"Satellite image for {location.capitalize()} saved as {output_filename}")