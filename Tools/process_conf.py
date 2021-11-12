# -------------------------------------------------------------------------------
# Name:        Process Configuration
# Purpose:     Enables to define Process related times in a machine readable manner
#
# Author:      kristjan.vilgo
#
# Created:     2021-10-28
# Copyright:   (c) kristjan.vilgo 2021
# Licence:     MIT
# -------------------------------------------------------------------------------


import time_helper

reference_times = {
    "currentHourStart": time_helper.get_hour_start,
    "currentDayStart": time_helper.get_day_start,
    "currentWeekStart": time_helper.get_week_start,
    "currentMonthStart": time_helper.get_month_start,
    "currentYearStart": time_helper.get_year_start
}

time_frames = {
    "ID": {
        "description": "Process running continuously within given day",
        "reference_time": "currentDayStart",
        "period_start": "P0D",
        "period_duration": "P1D"
    },
    "H-8": {
            "description": "Process running 8 hours ahead in intraday",
            "reference_time": "currentHourStart",
            "period_start": "PT1H",
            "period_duration": "PT8H"
        },
    "D-1": {
        "description": "Process that runs day before the targeted day",
        "reference_time": "currentDayStart",
        "period_start": "P1D",
        "period_duration": "P1D"
    },
    "D-2": {
        "description": "Process that runs two days before the targeted day",
        "reference_time": "currentDayStart",
        "period_start": "P2D",
        "period_duration": "P1D"
    },
    "D-7": {
        "description": "Process that runs day before the targeted day and covers time window of 7 days",
        "reference_time": "currentDayStart",
        "period_start": "P1D",
        "period_duration": "P7D"
    },
    "W-0": {
        "description": "Process that runs for current week",
        "reference_time": "currentWeekStart",
        "period_start": "P0W",
        "period_duration": "P1W"
    },
    "W-1": {
        "description": "Process that runs in current week for next week",
        "reference_time": "currentWeekStart",
        "period_start": "P1W",
        "period_duration": "P1W"
    },
    "M-1": {
        "description": "Process that runs in current month for next month",
        "reference_time": "currentMonthStart",
        "period_start": "P1M",
        "period_duration": "P1M"
    },
    "Y-1": {
        "description": "Process that runs in current year for next year",
        "reference_time": "currentYearStart",
        "period_start": "P1Y",
        "period_duration": "P1Y"
    }
}

business_processes = {
    "IGM_CREATION": {
        "description": "IGM creation and submission process",
        "time_zone": "Europe/Brussels",
        "responsible_role": "TSO",
        "quality_portal": "https://qas.opde.entsoe.eu/",
        "support_email": "opde.support@entsoe.eu",
    },
    "CGM_CREATION": {
        "description": "CGM creation and submission process",
        "time_zone": "Europe/Brussels",
        "responsible_role": "RSC",
        "responsible_group": "Operator",
        "quality_portal": "https://qas.opde.entsoe.eu/",
        "support_email": "opde.support@entsoe.eu",

    }

}

process_runs = [
    {
        "identification": "IntraDayIGM",
        "time_frame": "H-8",
        "business_process": "IGM_CREATION",
        "gate_open":  "PT1H30M",
        "gate_close": "PT1H",
        "gate_cutoff": "PT55M",
        "run_at": "02 07,15,23 * * *",
        "data_timestamps": "30 * * * *",
        "data_resolution": "PT1H"
    },
    {
        "identification": "DayAheadIGM",
        "time_frame": "D-1",
        "business_process": "IGM_CREATION",
        "gate_open":  "PT7H30M",
        "gate_close": "PT6H",
        "gate_cutoff": "PT5H10",
        "run_at": "40 16 * * *",
        "data_timestamps": "30 * * * *",
        "data_resolution": "PT1H"
    },
    {
        "identification": "TwoDaysAheadIGM",
        "time_frame": "D-2",
        "business_process": "IGM_CREATION",
        "gate_open":  "P1DT6H30M",
        "gate_close": "P1DT5H",
        "gate_cutoff": "P1DT4H10",
        "run_at": "40 17 * * *",
        "data_timestamps": "30 * * * *",
        "data_resolution": "PT1H"
    },
    {
        "identification": "IntraDayCGM",
        "time_frame": "H-8",
        "business_process": "CGM_CREATION",
        "gate_open":  "PT1H",
        "gate_close": "PT45M",
        "run_at": "05 07,15,23 * * *",
        "data_timestamps": "30 * * * *",
        "data_resolution": "PT1H"
    },
    {
        "identification": "DayAheadCGM",
        "time_frame": "D-1",
        "business_process": "CGM_CREATION",
        "gate_open":  "PT6H",
        "gate_close": "PT5H",
        "run_at": "50 18 * * *",
        "data_timestamps": "30 * * * *",
        "data_resolution": "PT1H"
    },
    {
        "identification": "TwoDaysAheadCGM",
        "time_frame": "D-2",
        "business_process": "CGM_CREATION",
        "gate_open":  "P1DT5H",
        "gate_close": "P1DT4H",
        "run_at": "50 19 * * *",
        "data_timestamps": "30 * * * *",
        "data_resolution": "PT1H"
    }
]
