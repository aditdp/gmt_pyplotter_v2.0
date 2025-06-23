grid_res = [
    "01s",
    "03s",
    "15s",
    "30s",
    "01m",
    "02m",
    "03m",
    "04m",
    "05m",
    "06m",
    "10m",
    "15m",
    "20m",
    "30m",
    "01d",
]

grid_source = [
    "Earth Relief v2.6 [SRTM15]",
    "Earth Relief v2.0 [SYNBATH]",
    "Earth Relief 2024 [GEBCO]",
    "Earth Seafloor Age [EarthByte]",
    "Earth Day View [Blue Marble]",
    "Earth Night View [Black Marble]",
    "Earth Magnetic Anomalies at sea-level [EMAG2v3]",
    "Earth Magnetic Anomalies at 4km altitude [EMAG2v3]",
    "Earth Magnetic Anomalies v2.1 [WDMAM]",
    "Earth Vertical Gravity Gradient Anomalies v32 [IGPP]",
    "Earth Free Air Gravity Anomalies v32 [IGPP]",
    "Earth Free Air Gravity Anomalies Errors v32 [IGPP]",
]

grid_data = {
    grid_source[1]: ["@earth_synbath_"] + grid_res,
    grid_source[2]: ["@earth_gebco_"] + grid_res,
    grid_source[3]: ["@earth_age_"] + grid_res[4:],
    grid_source[4]: ["@earth_day_"] + grid_res[3:],
    grid_source[5]: ["@earth_night"] + grid_res[3:],
    grid_source[0]: ["@earth_relief_"] + grid_res,
    grid_source[6]: ["@earth_mag_"] + grid_res[5:],
    grid_source[7]: ["@earth_mag4km_"] + grid_res[5:],
    grid_source[8]: ["@earth_wdmam_"] + grid_res[6:],grid_res,
    grid_source[11]: ["@earth_faaerror_"] + grid_res[4:],
}


print(grid_data[grid_source[2]][1:])
