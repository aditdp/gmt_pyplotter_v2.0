import os, sys, subprocess, csv, math
from datetime import datetime, timedelta
from dateutil import parser
from typing import Union, Dict
from urllib.request import urlretrieve, urlopen
from urllib.error import URLError


def open_file_default_app(messagebox,file_to_open):
    try:
        if sys.platform == "win32":
            os.startfile(file_to_open)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", file_to_open])
        else:
            subprocess.Popen(["xdg-open", file_to_open])
    except FileNotFoundError as e:
        messagebox.showerror(
            "Error", f"Could not open file: {e}\nIs '{file_to_open}' avalid path?"
        )
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
def file_writer(output_file: str, flag: str, text: str):
    with open(output_file, flag, encoding="utf-8") as file:
        file.write(text)


def file_is_not_empty(filename):
    if os.path.getsize(filename) != 0:
        return True
    else:
        print("No earthquake event found..")
        return False


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
                    continue

                try:
                    num_val = float(values[column_index].strip())
                    data.append(num_val)
                except ValueError:
                    continue
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {"Error": 0}
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return {"Error": 0}

    if not data:
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

    if trim_percentage > 0:
        trim_elements_count = int(len(data) * trim_percentage)
        sorted_data = sorted(data)

        if len(sorted_data) < 2 * trim_elements_count + 1:
            trimmed_data = sorted_data
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
                    continue

                try:
                    date_val = parser.parse(values[column_index].strip(), ignoretz=True)
                    data.append(date_val)
                except (ValueError, parser.ParserError):
                    continue
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

    if not data:
        return None

    minimum = min(data)
    maximum = max(data)
    full_range = maximum - minimum

    info = {
        "min": minimum,
        "max": maximum,
        "count": line_count,
        "range": full_range,
    }

    return info


def gcmt_downloader(dir_name, coord, date: list[datetime], mag, depth, queue):

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

        print(data_gcmt)
        file_writer(f"{dir_name}_ORI.txt", "w", data_gcmt)
        if file_is_not_empty(f"{dir_name}_ORI.txt"):
            add_mag_to_meca_file(
                f"{dir_name}_ORI.txt",
                f"{dir_name}.txt",
            )

            print("done..")
            msg = "Focal mechanism data succesfully downloaded"
            queue.put(("COMPLETE", msg))
        else:
            msg = "No focal mechanism found, change the search parameters"
            queue.put(("FAILED", msg))

    except URLError:
        msg = "Failed connecting to GlobalCMT data server.."
        print(msg)
        queue.put(("FAILED", msg))


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

                mrr = float(row[3])
                mtt = float(row[4])
                mpp = float(row[5])
                mrt = float(row[6])
                mrp = float(row[7])
                mtp = float(row[8])
                iexp = int(row[9])

                # Calculate Mw
                mw = calculate_mw(mrr, mtt, mpp, mrt, mrp, mtp, iexp)

                # Write the new row with Mw appended
                writer.writerow(row + [mw])
            except ValueError as e:
                print(f"    Error processing row: {row}. Error: {e}")


def usgs_downloader(dir_name: str, coord, date: list[datetime], mag, depth, queue):
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

            msg = "USGS catalog data succesfully downloaded"
            queue.put(("COMPLETE", msg))
        else:
            msg = "No data found, change the search parameters"
            queue.put(("FAILED", msg))

    except URLError:
        msg = "Failed connecting to USGS data server.."
        print(msg)
        queue.put(("FAILED", msg))


def isc_downloader(dir_name, coord, date: list[datetime], mag, depth, queue):

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
    print(f"retrieving data from:\n{url}")
    print("\n\nMay be take some time ..")
    try:
        page = urlopen(url)
        html = page.read().decode("utf-8")
        start_index = html.rfind("EVENTID") - 2
        end_index = html.rfind("STOP") - 1
        data_isc = html[start_index:end_index]
        print("data acquired..")
        file_writer(f"{dir_name}_ORI.txt", "w", data_isc)
        if file_is_not_empty(f"{dir_name}_ORI.txt"):
            reorder_columns(
                f"{dir_name}_ORI.txt",
                f"{dir_name}.txt",
                [6, 5, 7, 11, 3, 4],
            )
            print("done..")

            msg = "ISC catalog data succesfully downloaded"
            queue.put(("COMPLETE", msg))
        else:
            msg = "No data found, change the search parameters"
            queue.put(("FAILED", msg))

    except URLError:
        msg = "Failed connecting to ISC data server.."
        print(msg)
        queue.put(("FAILED", msg))


match os.name:
    case "posix":
        shel = True
    case "nt":
        shel = False


relief_0 = "Very Low Relief"
relief_1 = "Low to Moderate Relief"
relief_2 = "Moderate to High Relief"
relief_3 = "Very High Relief"


def categorize_scale(map_scale_factor):
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
    return scale_category


def categorize_relief(total_relief):
    relief_category = ""
    if total_relief < 100:
        relief_category = relief_0
    elif 100 <= total_relief < 1000:
        relief_category = relief_1
    elif 1000 <= total_relief < 2000:
        relief_category = relief_2
    else:  # total_relief >= 2000
        relief_category = relief_3
    print(relief_category)
    return relief_category


def divisor_vls(relief_category):
    if relief_category == relief_0:
        divisor = 20
    else:
        divisor = 40
    return divisor


def divisor_ls(relief_category):
    if relief_category == relief_0:
        divisor = 10
    elif relief_category == relief_1:
        divisor = 15
    elif relief_category == relief_2:
        divisor = 40
    else:
        divisor = 50
    return divisor


def divisor_ms(relief_category):
    if relief_category == relief_0:
        divisor = 10
    elif relief_category == relief_1:
        divisor = 15
    else:
        divisor = 20
    return divisor


def divisor_ss(relief_category):
    if relief_category == relief_0:
        divisor = 5
    elif relief_category == relief_1:
        divisor = 7.5
    elif relief_category == relief_2:
        divisor = 10
    else:
        divisor = 12.5
    return divisor


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
    scale_category = categorize_scale(map_scale_factor)
    relief_category = categorize_relief(total_relief)

    divisor = 1

    standard_cis = [5, 10, 12.5, 20, 25, 50, 75, 100, 150, 200, 250, 500]

    if scale_category == "Very Large Scale":
        divisor = divisor_vls(relief_category)
    elif scale_category == "Large Scale":
        divisor = divisor_ls(relief_category)
    elif scale_category == "Medium Scale":
        divisor = divisor_ms(relief_category)
    else:
        divisor = divisor_ss(relief_category)

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


def grdimage_min_max_interval(grd_: str, coord_r: str):
    """Evaluate the grd_file and return the recomended interval for cpt, elevmin, and elevmax"""
    command = f"gmt grdinfo {grd_}_p {coord_r} -Cn -M -G --GMT_DATA_SERVER=singapore"
    print(command)
    try:
        min_, max_, _ = grdimage_min_max(grd_, command)
        elevmin = round(float(min_), -1)
        elevmax = round(float(max_), -1)
        total_elev = elevmax - elevmin
        interval = 0
        if total_elev in range(5000, 20000):
            interval = 1000
        elif total_elev in range(2500, 5000):
            interval = 500
        elif total_elev in range(1000, 2500):
            interval = 250
        elif total_elev in range(500, 1000):
            interval = 100
        elif total_elev in range(0, 500):
            interval = 50
        return elevmin, elevmax, interval
    except subprocess.CalledProcessError:
        print("Error calc min-max values")
        return [0]
    except ConnectionError as e:
        print(e)
        return [0]
    except ValueError as e:
        print(e)
        return [0]


def grdimage_min_max(grd_, command):
    est_min_max = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        universal_newlines=True,
    )
    stdout, stderr = est_min_max.communicate()
    print(stdout)
    return_code = est_min_max.returncode
    grdinfo = stdout.split("\t")
    if "Unable to obtain remote file" in stderr:
        message = f"Couldn't connect to GMT remote server for downloading {grd_} data.\nConnect to internet or change network connection."
        raise ConnectionError(message)
    min_ = grdinfo[5]
    max_ = grdinfo[6]
    if min_.lower() == "nan" or max_.lower() == "nan":
        raise ValueError(f"No data {grd_} in this area..\nChoose another grid data.")
    min_ = float(grdinfo[4])
    max_ = float(grdinfo[5])
    print("dari utils")
    print(f"min = {min_}")
    print(f"max = {max_}")

    return min_, max_, return_code
