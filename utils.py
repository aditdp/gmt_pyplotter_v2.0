import os, subprocess, csv, math, threading, math, queue
from datetime import datetime, timedelta
from dateutil import parser
from typing import Union, Dict, Any
from urllib.request import urlretrieve, urlopen
from urllib.error import URLError
from PIL import Image


def file_writer(output_file: str, flag: str, text: str):
    with open(output_file, flag, encoding="utf-8") as file:
        file.write(text)


def file_is_not_empty(filename):
    return os.path.getsize(filename) != 0


def longitude_to_km(longitude_degrees_diff: float, latitude_degrees: float) -> float:
    """
    Converts a difference in longitude (in degrees) to a distance in kilometers
    at a specific latitude.

    Args:
        longitude_degrees_diff (float): The difference in longitude in degrees.
                                        Can be positive or negative.
        latitude_degrees (float): The latitude in degrees (from -90 to 90).

    Returns:
        float: The equivalent distance in kilometers.
                Returns 0.0 if input latitude is outside the valid range.
    """
    # Earth's approximate radius in kilometers
    # Using the WGS84 semi-major axis for a more common geodetic reference
    EARTH_RADIUS_KM = 6378.137

    # Validate latitude input
    if not (-90 <= latitude_degrees <= 90):
        print("Warning: Latitude must be between -90 and 90 degrees. Returning 0 km.")
        return 0.0

    # Convert latitude from degrees to radians for trigonometric functions
    latitude_radians = math.radians(latitude_degrees)

    # Calculate the length of one degree of longitude at the given latitude
    # The length of a degree of longitude is proportional to the cosine of the latitude.
    # Formula: (pi/180) * R * cos(latitude_radians)
    # Where:
    #   pi/180 converts degrees to radians for the 1-degree difference
    #   R is the Earth's radius
    #   cos(latitude_radians) accounts for the convergence of meridians at poles
    length_of_one_degree_longitude_at_latitude = (
        (math.pi / 180) * EARTH_RADIUS_KM * math.cos(latitude_radians)
    )

    # Calculate the total distance
    distance_km = (
        abs(longitude_degrees_diff) * length_of_one_degree_longitude_at_latitude
    )

    return distance_km


def reorder_columns(input_file, output_file, new_order):
    with open(input_file, "r", encoding="utf-8") as infile:
        reader = csv.reader(infile)

        # Write reordered columns to new file
        with open(output_file, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile, delimiter="\t")
            for row in reader:
                reordered_row = [row[i].strip() for i in new_order]
                writer.writerow(reordered_row)


def find_numeric_stats(
    filename: str,
    column_index: int,
    delimiter: str = "\t",
    trim_percentage: float = 0.01,
) -> dict[str, float | int]:
    """
    Analyzes a specified column in a delimited file to find min, max, count, and range
    for numeric (float) data.
    Optionally, it can also calculate these statistics for trimmed data (removing a
    percentage from both ends).

    Args:
        filename (str): The path to the input file.
        column_index (int): The 0-based index of the column to analyze.
        delimiter (str, optional): The delimiter used in the file. Defaults to "\\t".
        trim_percentage (float, optional): The percentage of data to trim from EACH end
                                            (e.g., 0.05 for 5% from top and 5% from bottom).
                                            Defaults to 0.05.

    Returns:
        dict: A dictionary containing the following numeric statistics:
                - "min": Minimum float value
                - "max": Maximum float value
                - "count": Total number of lines processed
                - "range": max - min
                - "trim_min": Minimum value of trimmed data (if applicable)
                - "trim_max": Maximum value of trimmed data (if applicable)
                - "trim_range": trim_max - trim_min (if applicable)
        None: If the file is empty, no valid numeric data could be parsed, or the
                specified column is out of bounds for all lines.
    """

    line_count = 0
    data: list[float] = []

    try:
        with open(filename, "r") as file:
            for line in file:
                line_count += 1
                values = line.strip().split(delimiter)

                if column_index >= len(values):
                    continue  # Skip lines that don't have enough columns

                try:
                    # Attempt to parse as float
                    num_val = float(values[column_index].strip())
                    data.append(num_val)
                except ValueError:
                    # Skip lines that cannot be converted to float
                    continue
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {"Error": 0}
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return {"Error": 0}

    if not data:  # Check if any numeric data was successfully parsed
        return {"Error": 0}

    minimum = min(data)
    maximum = max(data)
    full_range = maximum - minimum

    info = {
        "min": minimum,
        "max": maximum,
        "count": line_count,
        "range": full_range,
    }

    # Trimming logic for numeric data
    if trim_percentage > 0:  # Only apply trim if percentage is positive
        trim_elements_count = int(len(data) * trim_percentage)
        sorted_data = sorted(data)

        if len(sorted_data) < 2 * trim_elements_count + 1:
            trimmed_data = sorted_data  # No effective trimming
            print(
                f"Warning: Not enough data points ({len(data)}) to trim {trim_percentage*100}% from each end. No trimming applied."
            )
        else:
            trimmed_data = sorted_data[trim_elements_count:-trim_elements_count]

        if not trimmed_data:
            print(
                "Warning: Trimmed data is empty after potential trimming. Cannot calculate trim_min/max/range."
            )
        else:
            trim_min = min(trimmed_data)
            trim_max = max(trimmed_data)
            trim_range = trim_max - trim_min

            info.update(
                {
                    "trim_min": round(trim_min, -1),
                    "trim_max": round(trim_max, -1),
                    "trim_range": trim_range,
                }
            )

    return info


def find_datetime_stats(
    filename: str,
    column_index: int,
    delimiter: str = "\t",
) -> Union[Dict[str, Union[datetime, timedelta, int]], None]:
    """
    Analyzes a specified column in a delimited file to find min, max, count, and range
    for datetime data. Trimming is not supported for datetime data.

    Args:
        filename (str): The path to the input file.
        column_index (int): The 0-based index of the column to analyze.
        delimiter (str, optional): The delimiter used in the file. Defaults to "\\t".

    Returns:
        dict: A dictionary containing the following datetime statistics:
              - "min": Minimum datetime value
              - "max": Maximum datetime value
              - "count": Total number of lines processed
              - "range": max - min (a timedelta object)
        None: If the file is empty, no valid datetime data could be parsed, or the
              specified column is out of bounds for all lines.
    """

    line_count = 0
    data: list[datetime] = []

    try:
        with open(filename, "r") as file:
            for line in file:
                line_count += 1
                values = line.strip().split(delimiter)

                if column_index >= len(values):
                    continue  # Skip lines that don't have enough columns

                try:
                    # Attempt to parse as datetime
                    date_val = parser.parse(values[column_index].strip(), ignoretz=True)
                    data.append(date_val)
                except (ValueError, parser.ParserError):
                    # Skip lines that cannot be converted to datetime
                    continue
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

    if not data:  # Check if any datetime data was successfully parsed
        return None

    minimum = min(data)
    maximum = max(data)
    full_range = maximum - minimum  # This naturally results in a timedelta

    info = {
        "min": minimum,
        "max": maximum,
        "count": line_count,
        "range": full_range,
    }

    return info


def gcmt_downloader(dir_name, coord, date: list[datetime], mag, depth):

    url_gcmt = "https://www.globalcmt.org/cgi-bin/globalcmt-cgi-bin/CMT5/form?itype=ymd&yr={}&mo={}&day={}&otype=ymd&oyr={}&omo={}&oday={}&lmw={}&umw={}&llat={}&ulat={}&llon={}&ulon={}&lhd={}&uhd={}&list=6".format(
        date[0].strftime("%Y"),
        date[0].strftime("%m"),
        date[0].strftime("%d"),
        date[1].strftime("%Y"),
        date[1].strftime("%m"),
        date[1].strftime("%d"),
        mag[0],
        mag[1],
        coord[2],
        coord[3],
        coord[0],
        coord[1],
        depth[0],
        depth[1],
    )

    print(f"  retrieving data from:\n {url_gcmt}")
    try:
        page = urlopen(url_gcmt)
        html = page.read().decode("utf-8")
        start_index = html.rfind("<pre>") + 6
        end_index = html.rfind("</pre>")
        data_gcmt = html[start_index:end_index]
        print("data acquired..")
        # input("press any key to continue..")
        print(data_gcmt)
        file_writer(f"{dir_name}_ORI.txt", "w", data_gcmt)
        if file_is_not_empty(f"{dir_name}_ORI.txt"):
            add_mag_to_meca_file(
                f"{dir_name}_ORI.txt",
                f"{dir_name}.txt",
            )

            print("done..")
            status = "good"
        else:
            print("   No earthquake event found..")
            status = "empty"
        return status
    except URLError:
        print("Cannot connect to GlobalCMT data server..")
        print("Check your internet connection!")


def calculate_mw(mrr, mtt, mpp, mrt, mrp, mtp, iexp):
    """# Calculate the seismic moment M0"""
    m0 = (
        math.sqrt(0.5 * (mrr**2 + mtt**2 + mpp**2 + 2 * (mrt**2 + mrp**2 + mtp**2)))
        * 10**iexp
    )
    # Calculate the moment magnitude Mw
    mw = (2 / 3) * math.log10(m0) - 10.7
    return round(mw, 1)


def add_mag_to_meca_file(input_file, output_file, delimiter=" ", output_delimiter="\t"):
    """read the input file and insert the Mw value to the last column of meca file and save as output file name"""
    with open(input_file, "r") as infile, open(output_file, "w", newline="") as outfile:
        reader = csv.reader((line.rstrip() for line in infile), delimiter=delimiter)
        writer = csv.writer(outfile, delimiter=output_delimiter)

        # Process each row and calculate Mw
        for row in reader:
            try:
                # Check if row is correctly split
                if len(row) != 13:
                    raise ValueError("Row does not contain exactly 13 values")

                lon = float(row[0])
                lat = float(row[1])
                depth = float(row[2])
                mrr = float(row[3])
                mtt = float(row[4])
                mpp = float(row[5])
                mrt = float(row[6])
                mrp = float(row[7])
                mtp = float(row[8])
                iexp = int(row[9])
                x = row[10]
                y = row[11]
                name = row[12]

                # Calculate Mw
                mw = calculate_mw(mrr, mtt, mpp, mrt, mrp, mtp, iexp)

                # Write the new row with Mw appended
                writer.writerow(row + [mw])
            except ValueError as e:
                print(f"    Error processing row: {row}. Error: {e}")


def usgs_downloader(
    dir_name: str,
    coord,
    date: list[datetime],
    mag,
    depth,
):
    print("download usgs catalog")
    print(f"file path = {dir_name}")
    print(f"coord= {coord}")
    print(f"date = {date}")
    print(f"mag={mag}")
    print(f"depth={depth}")
    _start = date[0].strftime("%Y-%m-%d")
    _end = date[1].strftime("%Y-%m-%d")
    url_usgs = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv"
    url_loc = f"minlongitude={coord[0]}&maxlongitude={coord[1]}&minlatitude={coord[2]}&maxlatitude={coord[3]}"
    url_date = f"starttime={_start}&endtime={_end}"
    url_mag = f"minmagnitude={mag[0]}&maxmagnitude={mag[1]}"
    url_dep = f"mindepth={depth[0]}&maxdepth={depth[1]}"
    url = f"{url_usgs}&{url_date}&{url_loc}&{url_mag}&{url_dep}"
    print(url)
    print(f"\nRetrieving data from: {url}")
    print("\n    This may take a while...")
    try:
        urlretrieve(url, f"{dir_name}_ORI.txt")
        if file_is_not_empty(f"{dir_name}_ORI.txt"):

            reorder_columns(
                f"{dir_name}_ORI.txt",
                f"{dir_name}.txt",
                [2, 1, 3, 4, 0],
            )
            print("\n Done.. \n")
            status = "good"
        else:
            print("   No earthquake event found..")
            status = "empty"
        return status
    except URLError:
        print("Cannot connect to USGS data server..")
        print("Check your internet connection!")


def isc_downloader(dir_name, coord, date: list[datetime], mag, depth):

    url_isc = "https://www.isc.ac.uk/cgi-bin/web-db-run?request=COMPREHENSIVE&out_format=CATCSV&searchshape=RECT"

    url_loc = "&bot_lat={}&top_lat={}&left_lon={}&right_lon={}".format(
        coord[2],
        coord[3],
        coord[0],
        coord[1],
    )
    url_date = "&start_year={}&start_month={}&start_day={}&end_year={}&end_month={}&end_day={}".format(
        date[0].strftime("%Y"),
        date[0].strftime("%m"),
        date[0].strftime("%d"),
        date[1].strftime("%Y"),
        date[1].strftime("%m"),
        date[1].strftime("%d"),
    )
    url_dep = "&min_dep={}&max_dep={}&min_mag={}&max_mag={}".format(
        depth[0],
        depth[1],
        mag[0],
        mag[1],
    )
    url = url_isc + url_loc + url_date + url_dep
    print(f"\nEq data save as {dir_name}\n")
    # input("pause")
    print(f"retrieving data from:\n{url}")
    print("\n\nMay be take some time ..")
    try:
        page = urlopen(url)
        html = page.read().decode("utf-8")
        start_index = html.rfind("EVENTID") - 2
        end_index = html.rfind("STOP") - 1
        data_isc = html[start_index:end_index]
        print("data acquired..")
        # input("press any key to continue..")
        # print(data_isc)
        file_writer(f"{dir_name}_ORI.txt", "w", data_isc)
        if file_is_not_empty(f"{dir_name}_ORI.txt"):
            reorder_columns(
                f"{dir_name}_ORI.txt",
                f"{dir_name}.txt",
                [6, 5, 7, 11, 3, 4],
            )
            print("done..")
            status = "good"
        else:
            print("   No earthquake event found..")
            status = "empty"
        return status
    except URLError:
        print("Cannot connect to ISC data server..")
        print("Check your internet connection!")


match os.name:
    case "posix":
        shel = True
    case "nt":
        shel = False


def gmt_execute(script_name, output_dir, folowing: list):
    cwd = os.getcwd()
    os.chdir(output_dir)
    match os.name:
        case "nt":
            command = f"{script_name}.bat"
        case _:
            os.system(f"chmod +x {output_dir}/{script_name}.gmt")
            command = f"./{script_name}.gmt"

    try:
        print(f"Running '{output_dir}/{script_name}.bat' with subprocess.Popen()...")
        # exit_code = os.system(f"{name}.bat")
        generate_map = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = generate_map.communicate()
        return_code = generate_map.returncode
        print(
            f"[{threading.current_thread().name}] Process finished with code: {return_code}"
        )
        if return_code is not None:
            if return_code == 0:
                for i in folowing:
                    _ = i

        # penerusnya apa
    except FileNotFoundError:
        print(
            f"[{threading.current_thread().name}] Error: Program '{command}' not found."
        )

    except Exception as e:
        f"[{threading.current_thread().name}] An error occurred: {e}"
    os.chdir(cwd)


def recommend_contour_interval(map_scale_factor, min_value, max_value):

    if not isinstance(map_scale_factor, (int, float)) or map_scale_factor <= 0:
        return None
    if not isinstance(min_value, (int, float)) or not isinstance(
        max_value, (int, float)
    ):
        return None
    if min_value >= max_value:
        return None

    total_relief = max_value - min_value
    print("total relief=", total_relief)
    scale_category = ""
    if map_scale_factor < 50000:
        scale_category = "Very Large Scale"
    elif 50000 <= map_scale_factor <= 500000:
        scale_category = "Large Scale"
    elif 500000 < map_scale_factor <= 2000000:
        scale_category = "Medium Scale"
    else:  # map_scale_denominator > 2000000
        scale_category = "Small Scale"
    print(scale_category)
    relief_category = ""
    if total_relief < 100:
        relief_category = "Very Low Relief"
    elif 100 <= total_relief < 1000:
        relief_category = "Low to Moderate Relief"
    elif 1000 <= total_relief < 2000:
        relief_category = "Moderate to High Relief"
    else:  # total_relief >= 2000
        relief_category = "Very High Relief"
    print(relief_category)
    divisor = 1

    standard_cis = [5, 10, 12.5, 20, 25, 50, 75, 100, 150, 200, 250, 500]

    if scale_category == "Very Large Scale":
        if relief_category == "Very Low Relief":
            divisor = 10

        elif relief_category == "Low to Moderate Relief":
            divisor = 40

        else:  # Moderate to High / Very High Relief
            divisor = 40

    elif scale_category == "Large Scale":
        if relief_category == "Very Low Relief":
            divisor = 10

        elif relief_category == "Low to Moderate Relief":
            divisor = 15

        elif relief_category == "Moderate to High Relief":
            divisor = 40

        else:  # Very High Relief (Mountainous)
            divisor = 50

    elif scale_category == "Medium Scale":
        if relief_category == "Very Low Relief":
            # Very flat terrain is rarely mapped at medium scales for detailed contours
            divisor = 10

        elif relief_category == "Low to Moderate Relief":
            divisor = 15

        elif relief_category == "Moderate to High Relief":
            divisor = 20

        else:  # Very High Relief (Mountainous)
            divisor = 20

    else:  # scale_category == "Small Scale"
        if relief_category == "Very Low Relief":
            # Very flat terrain is almost never mapped with contours at small scales
            divisor = 5

        elif relief_category == "Low to Moderate Relief":
            divisor = 7.5

        elif relief_category == "Moderate to High Relief":
            divisor = 10

        else:  # Very High Relief (Mountainous)
            divisor = 12.5
    recommended_ci = total_relief / divisor
    print(recommended_ci)
    if recommended_ci is not None:
        closest_ci = min(standard_cis, key=lambda x: abs(x - recommended_ci))
        recommended_ci = closest_ci

    return recommended_ci


RECOMMENDED_DEM_RESOLUTION = [
    (50000, "01s"),
    (150000, "03s"),
    (700000, "15s"),
    (2000000, "30s"),
    (4000000, "01m"),
    (6000000, "02m"),
    (8000000, "03m"),
    (10000000, "05m"),
    (12500000, "10m"),
    (25000000, "15m"),
    (50000000, "30m"),
    (float("inf"), "01d"),
]


def recommend_dem_resolution(map_scale_factor, for_contour=False):
    """
    Recommends a suitable DEM resolution (in a standard format like "01s", "05m", or "01d")
    based on the map scale.

    Args:
        map_scale_denominator (int): The denominator of the map's representative fraction scale
                                     (e.g., 10000 for 1:10000).

    Returns:
        str: The recommended DEM resolution in string format, or '01m' if input is invalid'.
    """

    if not isinstance(map_scale_factor, (int, float)) or map_scale_factor <= 0:
        return "01m"

    initial_dem_res_index = -1
    for i, (threshold, _) in enumerate(RECOMMENDED_DEM_RESOLUTION):
        if map_scale_factor <= threshold:
            initial_dem_res_index = i
            break

    # If map_scale_factor is larger than all defined thresholds, use the coarsest resolution
    if initial_dem_res_index == -1:
        initial_dem_res_index = len(RECOMMENDED_DEM_RESOLUTION) - 1

    # Get the base recommended resolution string
    recommended_res_string = RECOMMENDED_DEM_RESOLUTION[initial_dem_res_index][1]

    # Apply the "one level above" condition for contour generation
    if for_contour:
        # If there's a coarser resolution available in the list, use it.
        # Otherwise, stick with the current (coarsest) resolution.
        if initial_dem_res_index + 1 < len(RECOMMENDED_DEM_RESOLUTION):
            recommended_res_string = RECOMMENDED_DEM_RESOLUTION[
                initial_dem_res_index + 1
            ][1]

    return recommended_res_string
