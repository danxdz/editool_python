# Tolerance table for ISO metric threads
# Each key is a (pitch, class, thread_type), and values are tolerances
TOLERANCE_TABLE = {
    # (pitch, class, thread_type): (major_tolerance, pitch_tolerance, minor_tolerance)
    (1.5, "6H", "internal"): (0.428, 0.212, 0.300),
    (1.5, "6g", "external"): (0.150, 0.160, 0.434),
    # Add more entries for other pitches and classes as needed
}

def calculate_thread_dimensions(diameter, pitch, tolerance_class, thread_type):
    """
    Calculate thread dimensions for internal or external threads using the tolerance table.
    """
    # Fetch tolerances from the table
    tolerances = TOLERANCE_TABLE.get((pitch, tolerance_class, thread_type))
    if not tolerances:
        raise ValueError(f"Tolerances not found for pitch {pitch}, class {tolerance_class}, type {thread_type}")
    
    tolerance_major, tolerance_pitch, tolerance_minor = tolerances

    # Calculate dimensions based on the formulas for ISO metric threads
    # M55x1.5 6H internal thread example
    #Minor Diameter (D1) 
    #D1min = 53.376 D1max = 53.676

    #Pitch Diameter (D2)
    #D2min = 54.026 D2max = 54.238

    #Major Diameter (D)
    #D = 55.000 Dmax = 55.428

    # M55x1.5 6g external thread example
    #Minor Diameter (D1)
    #D1max = 53.344 D1min = 52.91
    #Pitch Diameter (D2)
    #D2max = 53.99 D2min = 53.83
    #Major Diameter (D)
    #D = 54.97 Dmin = 54.73 


    if thread_type == "internal":
        
        d1_min = diameter - 1.08253 * pitch
        d1_max = d1_min + tolerance_minor

        d2_min = diameter - 0.64952 * pitch
        d2_max = d2_min + tolerance_pitch

        d_min = diameter
        d_max = diameter + tolerance_major
    else:
        d1_max = diameter - 1.08253 * pitch
        d1_min = d1_max - tolerance_minor

        d2_max = diameter - 0.64952 * pitch
        d2_min = d2_max - tolerance_pitch

        d_max = diameter
        d_min = diameter - tolerance_major

    # Return results
    return {
        "D1_min": d1_min, "D1_max": d1_max,
        "D2_min": d2_min, "D2_max": d2_max,
        "D_min": d_min, "D_max": d_max
    }

# Example usage
thread_designations = [
    #{"diameter": 55, "pitch": 1.5, "class": "6H", "thread_type": "internal"},
    {"diameter": 55, "pitch": 1.5, "class": "6g", "thread_type": "external"}
]



# Print header
print(f"{'Thread':<12} {'Type':<8} {'Class':<6} {'D1 min':<10} {'D1 max':<10} {'D2 min':<10} {'D2 max':<10} {'D min':<10} {'D max':<10}")

# Calculate and print results
for thread in thread_designations:
    dimensions = calculate_thread_dimensions(thread['diameter'], thread['pitch'], thread['class'], thread['thread_type'])
    print(f"M{thread['diameter']}x{thread['pitch']:<6} "
          f"{thread['thread_type']:<8} {thread['class']:<6} "
          f"{dimensions['D1_min']:<10.3f} {dimensions['D1_max']:<10.3f} "
          f"{dimensions['D2_min']:<10.3f} {dimensions['D2_max']:<10.3f} "
          f"{dimensions['D_min']:<10.3f} {dimensions['D_max']:<10.3f}")
