
"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow

#  Note for CIS 322 Fall 2016:
#  You MUST provide the following two functions
#  with these signatures, so that I can write
#  automated tests for grading.  You must keep
#  these signatures even if you don't use all the
#  same arguments.  Arguments are explained in the
#  javadoc comments.
#

ACP_SPEEDS = [
    (200, 15, 34),
    (400, 15, 32),
    (600, 15, 30),
    (1000, 11.428, 28),
    (1300, 13.333, 26)
]

BREVET_LIMITS = {
    200: 13.5,
    300: 20,
    400: 27,
    600: 40,
    1000: 75
}


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """

    distance = min(float(control_dist_km), float(brevet_dist_km))

    # Starting control opens at the brevet start time
    start = arrow.get(brevet_start_time)

    if distance <= 0:
        return start.isoformat()

    total_hours = 0
    previous_limit = 0

    for limit, min_speed, max_speed in ACP_SPEEDS:
        segment = min(distance, limit) - previous_limit
        if segment > 0:
            total_hours += segment / max_speed
        previous_limit = limit
        if distance <= limit:
            break
    total_minutes = round(total_hours * 60)
    opening_time = start.shift(minutes=total_minutes)

    return opening_time.isoformat()


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
          brevet_dist_km: number, the nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """

    distance = min(float(control_dist_km), float(brevet_dist_km))
    start = arrow.get(brevet_start_time)

    if distance <= 60:
        total_hours = 1 + distance / 20
    else:
        total_hours = 0
        previous_limit = 0
        for limit, min_speed, max_speed in ACP_SPEEDS:
            segment = min(distance, limit) - previous_limit
            if segment > 0:
                total_hours += segment / min_speed
            previous_limit = limit
            if distance <= limit:
                break

    if distance >= float(brevet_dist_km):
        total_hours = BREVET_LIMITS[int(brevet_dist_km)]

    total_minutes = round(total_hours * 60)
    closing_time = start.shift(minutes=total_minutes)

    return closing_time.isoformat()
