RECOMMENDED_DEM_RESOLUTION_MAP = {
    # Map Scale Denominator Upper Bound : Recommended DEM Resolution String
    2000: "1s",  # For map scales up to 1:2000, recommend 1 arc-second resolution
    7500: "3s",  # For map scales up to 1:7500, recommend 3 arc-seconds resolution
    15000: "15s",  # For map scales up to 1:15000, recommend 15 arc-seconds resolution
    35000: "30s",  # For map scales up to 1:35000, recommend 30 arc-seconds resolution
    75000: "1m",  # For map scales up to 1:75000, recommend 1 arc-minute resolution
    150000: "2m",  # For map scales up to 1:150000, recommend 2 arc-minutes resolution
    250000: "3m",  # For map scales up to 1:250000, recommend 3 arc-minutes resolution
    500000: "5m",  # For map scales up to 1:500000, recommend 5 arc-minutes resolution
    1000000: "10m",  # For map scales up to 1:1000000, recommend 10 arc-minutes resolution
    2500000: "15m",  # For map scales up to 1:2500000, recommend 15 arc-minutes resolution
    5000000: "30m",  # For map scales up to 1:5000000, recommend 30 arc-minutes resolution
    float("inf"): "1deg",  # For any larger map scale, recommend 1 degree resolution
}


def recommend_dem_resolution(map_scale_denominator):
    """
    Recommends a suitable DEM resolution (in a standard format like "1s", "5m", or "1deg")
    based on the map scale.

    Args:
        map_scale_denominator (int): The denominator of the map's representative fraction scale
                                     (e.g., 10000 for 1:10000).

    Returns:
        str: The recommended DEM resolution in string format, or None if input is invalid.
    """

    if (
        not isinstance(map_scale_denominator, (int, float))
        or map_scale_denominator <= 0
    ):
        return None

    # Iterate through the sorted thresholds to find the appropriate resolution
    # The dictionary keys are already sorted in ascending order.
    for threshold, dem_res_string in RECOMMENDED_DEM_RESOLUTION_MAP.items():
        if map_scale_denominator <= threshold:
            return dem_res_string

    return None  # Should not be reached due to float('inf') as the last threshold
