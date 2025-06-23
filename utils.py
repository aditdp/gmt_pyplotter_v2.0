import os, shutil, sys, subprocess, time, cursor, csv, math, threading
from datetime import datetime, timedelta
from dateutil import parser
from functools import wraps
from urllib.request import urlretrieve, urlopen
from PIL import Image


def is_file_empty(filepath, filename):
    file = os.path.join(filepath, filename)
    return os.path.getsize(file) == 0


def reorder_columns(input_file, output_file, new_order):
    with open(input_file, "r", encoding="utf-8") as infile:
        reader = csv.reader(infile)

        # Write reordered columns to new file
        with open(output_file, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile, delimiter="\t")
            for row in reader:
                reordered_row = [row[i].strip() for i in new_order]
                writer.writerow(reordered_row)


def gcmt_downloader(fm_file, file_path, coord, date, mag, depth):

    url_gcmt = "https://www.globalcmt.org/cgi-bin/globalcmt-cgi-bin/CMT5/form?itype=ymd&yr={}&mo={}&day={}&otype=nd&nday={}&lmw={}&umw={}&llat={}&ulat={}&llon={}&ulon={}&lhd={}&uhd={}&list=6".format(
        date[0].strftime("%Y"),
        date[0].strftime("%m"),
        date[0].strftime("%d"),
        date[2],
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
    page = urlopen(url_gcmt)
    html = page.read().decode("utf-8")
    start_index = html.rfind("<pre>") + 6
    end_index = html.rfind("</pre>")
    data_gcmt = html[start_index:end_index]
    print("data acquired..")
    # input("press any key to continue..")
    print(data_gcmt)
    file_writer("w", f"{fm_file[0:-4]}_ORI.txt", data_gcmt, file_path)
    if is_file_empty(file_path, f"{fm_file[0:-4]}_ORI.txt") == False:
        add_mag_to_meca_file(
            os.path.join(file_path, f"{fm_file[0:-4]}_ORI.txt"),
            os.path.join(file_path, fm_file),
        )

        print("done..")
        status = "good"
    else:
        print("   No earthquake event found..")
        status = "empty"
    return status


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


def usgs_downloader(eq_file: str, file_path: str, coord, date, mag, depth):
    url_usgs = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv"
    url_loc = f"minlongitude={coord[0]}&maxlongitude={coord[1]}&minlatitude={coord[2]}&maxlatitude={coord[3]}"
    url_date = f"starttime={date[0]}&endtime={date[1]}"
    url_mag = f"minmagnitude={mag[0]}&maxmagnitude={mag[1]}"
    url_dep = f"mindepth={depth[0]}&maxdepth={depth[1]}"
    url = f"{url_usgs}&{url_date}&{url_loc}&{url_mag}&{url_dep}"
    print(f"\nRetrieving data from: {url}")
    print("\n    This may take a while...")
    urlretrieve(url, os.path.join(file_path, f"{eq_file[0:-4]}_ORI.txt"))
    if is_file_empty(file_path, f"{eq_file[0:-4]}_ORI.txt") == False:

        reorder_columns(
            os.path.join(file_path, f"{eq_file[0:-4]}_ORI.txt"),
            os.path.join(file_path, eq_file),
            [2, 1, 3, 4, 0],
        )
        print("\n Done.. \n")
        status = "good"
    else:
        print("   No earthquake event found..")
        status = "empty"
    return status


def isc_downloader(eq_file, file_path, coord, date, mag, depth):

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
    print(f"\nEq data save as {eq_file}\n")
    # input("pause")
    print(f"retrieving data from:\n{url}")
    print("\n\nMay be take some time ..")
    page = urlopen(url)
    html = page.read().decode("utf-8")
    start_index = html.rfind("EVENTID") - 2
    end_index = html.rfind("STOP") - 1
    data_isc = html[start_index:end_index]
    print("data acquired..")
    # input("press any key to continue..")
    # print(data_isc)
    file_writer("w", f"{eq_file[0:-4]}_ORI.txt", data_isc, file_path)
    if is_file_empty(file_path, f"{eq_file[0:-4]}_ORI.txt") == False:
        reorder_columns(
            os.path.join(file_path, f"{eq_file[0:-4]}_ORI.txt"),
            os.path.join(file_path, eq_file),
            [6, 5, 7, 11, 3, 4],
        )
        print("done..")
        status = "good"
    else:
        print("   No earthquake event found..")
        status = "empty"
    return status


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
