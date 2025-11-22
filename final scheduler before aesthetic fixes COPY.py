# Active Recall Schedule Generator:
#---
# Basic Rules:
# Topics can only be repeated with minimum 2 day gap
# Each M1 topic needs to be covered twice per week (monday-monday)
# Each Development topic needs to be covered twice per week (monday-monday)
# Each Biochem topic needs to be covered three times per week (monday-monday), with the exception of Chromatin below:
    # Rosana+Antoine in M1 need to be on the same day as Chromatin in Biochem
    # So Chromatin is covered only twice per week
# There can be 1-3 topics for Biochem and Development per day
# If the Development topic is StJohnston+Sanson then only 1 topic can be scheduled that day for development (does not affect other lists)
# ---
# Output Features:
# A coloured visual image of a monday - monday calendar
# Containing the list heading followed by the topics for each day grouped with bullet points
# This should automatically pop-up when the schedule is generated
# Could this also auto-update when 'shuffled'?
# ---
# Troubleshooting / Additional Features:
# Debug print statements to show the current state of the schedule as it is being built
# Checks to ensure that all topics are covered the required number of times
# Checks to ensure that no topic is missed or over-covered
# A shuffle function to generate a different valid schedule each time the program is run
    # Can this be an interactive shuffle button on the UI?
#---

# Importing packages
import random
from PIL import Image, ImageDraw, ImageFont
import os
import platform
import itertools 
from itertools import combinations
from collections import Counter


# Starting by defining a set M1 sequence for one topic a day for 8-days
M1_ORDER = ["Farr", 
            "Rosana+Antoine", 
            "Russel+Flicek", 
            "Segal", 
            "Farr", 
            "Rosana+Antoine", 
            "Russel+Flicek", 
            "Segal"
] 

# Setting up days as monday to monday
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday2"]

# Lists containing 'Topics'
# Biochem = 7 topics, Development = 7 topics, 
BIOCHEM = [
    "Transcription",
    "Chromatin",
    "RNA-localisation",
    "Alternative-Splicing",
    "Translation-I",
    "RNA-Turnover",
    "Translation II + Small-RNAs",
    "Nuclear-Coordination"
]
DEVELOPMENT = [
    "Santos+Scarpa",
    "StJohnston",
    "Sanson",
    "Ahringer",
    "Steventon",
    "Boroviak",
    "Clark",
    "Teixera"
]
 


# Setting repeat counts for individual topics
REPEAT_COUNTS = {
    #Biochem:
    "Transcription": 3,
    "Chromatin": 2,
    "Alternative-Splicing": 3,
    "Translation-I": 3,
    "RNA-Turnover": 3,
    "Translation II + Small-RNAs": 3,
    "RNA-localisation": 3,
    "Nuclear-Coordination": 3,
    #Development:
     
    "Santos+Scarpa": 2,
    "StJohnston": 2,
    "Sanson": 2,
    "Ahringer": 2,
    "Clark": 2,
    "Steventon": 2,
    "Boroviak": 2,
    "Teixera": 2,

    #M1:
    "Farr": 2,
    "Segal": 2,
    "Rosana+Antoine": 2,
    "Russel+Flicek": 2
}



# Parameters per list for scheduling
MIN_TOPICS_BIOCHEM = 2
MAX_TOPICS_BIOCHEM = 3
MIN_TOPICS_DEVELOPMENT = 2
MAX_TOPICS_DEVELOPMENT = 2
GAP = 2

# - shuffle = true does not impact no output
SHUFFLE = False

# Creating combinations for lists
# min_size = minimum number of topics in combination
# max_size = maximum number of topics in combination
# Returns a generator of tuples
def combos_of_topics(candidates, min_size, max_size):
    for size in range(min_size, max_size+1):
        yield from itertools.combinations(candidates, size)

def generate_schedule(attempts=None, verbose=True):
    attempt = 0
    while attempts is None or attempt < 1000:
        attempt += 1
        if verbose:
            print(f"\n--- Attempt {attempt} to generate schedule ---")
        # Generate schedule
        schedule = {day: {"Biochem": [], "Development": [], "M1": []} for day in DAYS}
        counter = Counter()
        last_seen = {t: -GAP-1 for t in REPEAT_COUNTS.keys()}


        # Debug step
        print("=== Initial Schedule Generation ===")
        print(f"DAYS: {DAYS}")
        print(f"M1_ORDER: {M1_ORDER}")
        print(f"BIOCHEM: {BIOCHEM}")
        print(f"DEVELOPMENT: {DEVELOPMENT}")
        print(f"REPEAT_COUNTS: {REPEAT_COUNTS}")
        print(f"GAP: {GAP}")

        # Fix M1 topics first
        for i, day in enumerate(DAYS):
            m1_topic = M1_ORDER[i]
            schedule[day]["M1"] = [m1_topic]
            counter[m1_topic] += 1
            last_seen[m1_topic] = i
            # Debug step
            if verbose:
                print(f"Assigned M1 topic '{m1_topic}' to {day}")

        
        # recursive backtracer, start with Biochem first then Development
        # so sort out Biochem combinations first
        def schedule_day(day_index, counter, last_seen):
            #biochem demans vs slots
            remaining_needed = sum(max(0, REPEAT_COUNTS[t] - counter[t]) for t in BIOCHEM)
            remaining_slots = (len(DAYS) - day_index) * MAX_TOPICS_BIOCHEM
            if remaining_needed > remaining_slots:
                if verbose:
                    print(f"Prune: remaining_needed={remaining_needed} > remaining_slots={remaining_slots} at day_index={day_index}")
                return False, counter
            # define chromatin rule
            chrom_remaining = max(0, REPEAT_COUNTS.get("Chromatin", 0) - counter.get("Chromatin", 0))
            rosana_remaining = sum(1 for i in range(day_index, len(DAYS)) if M1_ORDER[i] == "Rosana+Antoine")
            if chrom_remaining > rosana_remaining:
                if verbose:
                    print(f"Prune: chrom_remaining={chrom_remaining} > rosana_remaining={rosana_remaining} at day_index={day_index}")
                return False, counter
            
            if day_index >= len(DAYS):
                # verify if all repeat counts satisfied at the end
                for t, required in REPEAT_COUNTS.items():
                    if counter.get(t, 0) != required:
                        if verbose:
                            print(f"End check failed: {t} scheduled {counter.get(t,0)} vs required {required}")
                        return False, counter
                    if verbose:
                        print("reached end of DAYS - yay!")
                    return True, counter  # Successfully scheduled all days

            day = DAYS[day_index]
            m1_topic = schedule[day]["M1"][0]
            #Debug step
            if verbose:
                print(f"\nScheduling Day {day} (index {day_index}) with M1 topic '{m1_topic}'")
        

            # Biochem candidates
            b_candidates = [
                t for t in BIOCHEM
                if counter[t] < REPEAT_COUNTS[t] 
                and day_index - last_seen.get(t, -999) >= GAP
            ]

            # Debug step
            if verbose:
                print(f"Biochem candidates: {b_candidates}")

            # starting list prioritising by remaining demand
            today_biochem = []
        
        
            # Chromatin must be on days where M1 is Rosana+Antoine (but only if Chromatin still needs repeats)
            if m1_topic == "Rosana+Antoine" and counter.get("Chromatin", 0) < REPEAT_COUNTS.get("Chromatin", 0):
                today_biochem.append("Chromatin")
                if verbose:
                    print(f"Chromatin forced on {day} due to M1='{m1_topic}'")

            # Determine how many additional Biochem topics to choose this day
            min_b = max(MIN_TOPICS_BIOCHEM - len(today_biochem), 0)
            max_b = min(MAX_TOPICS_BIOCHEM - len(today_biochem), len(b_candidates))

            # If min_b > max_b there's no feasible pick for this day
            if min_b > max_b:
                if verbose:
                    print(f"No feasible number of Biochem picks for {day} (min_b={min_b}, max_b={max_b}) — backtrack")
                return False, counter

            # Generate Biochem combinations for this day
            biochem_combos = []
            for size in range(min_b, max_b + 1):
                biochem_combos.extend(itertools.combinations(b_candidates, size))

            # Score combos by remaining demand
            def combo_score(combo, base_counter = counter):
                return sum(REPEAT_COUNTS[t] - base_counter[t] for t in combo)
            biochem_combos.sort(key = lambda c: combo_score(c), reverse=True)

            # IF SHUFFLE, shuffle within equal score groups
            if SHUFFLE:
                grouped = {}
                for c in biochem_combos:
                    s = combo_score(c)
                    grouped.setdefaults(s, []).append(c)
                biochem_combos = []
                for s in sorted(grouped.keys(), reverse=True):
                    group = grouped[s]
                    random.shuffle(group)
                    biochem_combos.extend(group)
        

            if not biochem_combos and min_b > 0:
                if verbose:
                    print(f"No biochem combos and need min {min_b} — backtrack")
                return False, counter
        
            # Try each biochem combo and for each try dev combos with backtracking
            for combo in biochem_combos:
                temp_today_biochem = today_biochem + list(combo)
                # stop duplicates in same day:
                if len(set(temp_today_biochem)) < len(temp_today_biochem):
                    if verbose:
                        # Debug step
                        print(f"Skipping duplicate Biochem combo on {day}: {temp_today_biochem}")
                    continue
                # Update temporary counters for backtracking
                temp_counter = counter.copy()
                temp_last_seen = last_seen.copy()
                for t in temp_today_biochem:
                    temp_counter[t] += 1
                    temp_last_seen[t] = day_index

                # Skip combinations that go over repeat counts
                over = [t for t in temp_today_biochem if temp_counter[t] > REPEAT_COUNTS[t]]
                if over:
                    if verbose:
                        # Debug step
                        print(f"Skipping over-repeat Biochem combo on {day}: {temp_today_biochem} (over: {over})")
                    continue
            

            # Development candidates
                d_candidates = [t for t in DEVELOPMENT if temp_counter[t] < REPEAT_COUNTS[t] and day_index - temp_last_seen[t] >= GAP]

                # Debug step
                if verbose:
                    print(f"Development candidates for {day}: {d_candidates}")

                # Generate Development combinations
                dev_combos = []
                if d_candidates:
                    for size in range(MIN_TOPICS_DEVELOPMENT, min(MAX_TOPICS_DEVELOPMENT, len(d_candidates)) + 1):
                        dev_combos.extend(itertools.combinations(d_candidates, size))
                    
                
                # for shuffle function 
                if SHUFFLE:
                    random.shuffle(dev_combos) 

                for today_dev in dev_combos:
                    today_dev = list(today_dev)
                    # Debug step
                    print(f"Trying combination on {day}: Biochem={today_biochem}, Development={today_dev}")
                    # Update temporary counters for backtracking
                    temp_counter2 = temp_counter.copy()
                    temp_last_seen2 = temp_last_seen.copy()
                    for t in today_dev:
                        temp_counter2[t] += 1
                        temp_last_seen2[t] = day_index
                    # assign and recurse
                    schedule[day]["Biochem"] = temp_today_biochem
                    schedule[day]["Development"] = today_dev

                    # Debug step
                    if verbose:
                        print(f"Trying {day}: Biochem={temp_today_biochem}, Development={today_dev}")

                    success, final_counter = schedule_day(day_index + 1, temp_counter2, temp_last_seen2)
                    if success:
                        return True, final_counter
                    if verbose:
                        # Debug step
                        print(f"Backtracking from {day} with Biochem {today_biochem} and Development {today_dev}")
                
            # Backtrack happens automatically via temp_counter/temp_last_seen if no combination worked

            schedule[day]["Development"] = []
            schedule[day]["Biochem"] = []
            if verbose:
                # Debug step
                print(f"No valid combinations left for {day} — returning False")
            return False, counter
        # run backtracking attempt
        
            # vary RNG per attempt so that shuffle reorders differently between attempts
        if SHUFFLE:
            random.seed(attempt + int.from_bytes(os.urandom(2), "big"))
        success, final_counter = schedule_day(0, counter, last_seen)
        if success:
            if verbose:
                print(f"Schedule successfully generated in attempt {attempt}")
            return schedule, final_counter
        if verbose:
            print(f"Attempt {attempt} failed to generate a valid schedule.")

    raise RuntimeError("Failed to generate schedule within attempt limit")

# Validation Checks
def validate(schedule, counter):
    print("\n--- Repeat Validation ---")
    for topic, expected in REPEAT_COUNTS.items():
        actual = counter[topic]
        if actual != expected:
            print(f"WARNING: '{topic}' repeated {actual} times (expected {expected})")



    print("\n--- Minimum/Maximum Topics per Day ---")
    for day in DAYS:
        biochem_len = len(schedule[day]["Biochem"])
        dev_len = len(schedule[day]["Development"])
        m1_len = len(schedule[day]["M1"])
        if not (MIN_TOPICS_BIOCHEM <= biochem_len <= MAX_TOPICS_BIOCHEM):
            print(f"WARNING: Biochem topics on {day} = {biochem_len}")
        if not (MIN_TOPICS_DEVELOPMENT <= dev_len <= MAX_TOPICS_DEVELOPMENT and "StJohnston+Sanson" not in schedule[day]["Development"]):
            print(f"WARNING: Development topics on {day} = {dev_len}")
        if m1_len != 1:
            print(f"WARNING: M1 topics on {day} = {m1_len}")

# Print for console
def print_schedule(schedule):
    for day in DAYS:
        dayblock = schedule[day]
        total = len(dayblock["Biochem"]) + len(dayblock["Development"]) + len(dayblock["M1"])
        print(f"\n{day} — total topics: {total}")
        print("  Biochem:     ", ", ".join(dayblock["Biochem"]) if dayblock["Biochem"] else "—")
        print("  Development: ", ", ".join(dayblock["Development"]) if dayblock["Development"] else "—")
        print("  M1:          ", ", ".join(dayblock["M1"]) if dayblock["M1"] else "—")



# Create Calendar Image
def draw_calendar_image(schedule, filename="calendar.png"):
    dpi = 100
    border_inch = 2
    border_px = border_inch*dpi
    cols, rows = 3, len(DAYS)
    inner_width, inner_height = 1200, 900
    width, height = inner_width + 2*border_px, inner_height + 2*border_px
    col_width = inner_width // cols
    row_height = inner_height // rows
    colors = {'Biochem':'#FFCC99','Development':'#99CCFF','M1':'#CCFF99'}
    img = Image.new("RGB", (width,height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf",18)
        header_font = ImageFont.truetype("arial.ttf",22)
    except:
        font = ImageFont.load_default()
        header_font = ImageFont.load_default()

    for j, list_name in enumerate(['Biochem','Development','M1']):
        x = border_px + j*col_width + col_width//2
        y = border_px//2
        draw.text((x,y), list_name,font=header_font,anchor="ms",fill="black")

    for i, day in enumerate(DAYS):
        y_top = border_px + i*row_height
        y_bottom = y_top + row_height
        draw.text((border_px//2, y_top + row_height//2), day, font=header_font, anchor="ms", fill="black")
        for j, list_name in enumerate(['Biochem','Development','M1']):
            x_left = border_px + j*col_width
            x_right = x_left + col_width
            draw.rectangle([x_left,y_top,x_right,y_bottom], fill=colors[list_name], outline="black")
            topics = schedule[day][list_name]
            font_cell = adjust_font(draw, topics, col_width-20, row_height-20)
            draw_multiline_text(draw, "\n".join(topics), x_left+10, y_top+10, font_cell, max_width=col_width-20)
    img.save(filename)
    if platform.system() == "Windows":
        os.startfile(filename)
    else:
        img.show()

# -Calendar font helpers
def adjust_font(draw, topics, max_width, max_height, starting_size=18):
    font_size = starting_size
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
        return font
    line_spacing = 4
    while True:
        total_height = 0
        for t in topics:
            bbox = draw.textbbox((0,0), t, font=font)
            h = bbox[3]-bbox[1]
            total_height += h + line_spacing
        if total_height <= max_height or font_size <= 8:
            break
        font_size -= 1
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
            break
    return font

def draw_multiline_text(draw, text, x, y, font, max_width, line_spacing=4):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            bbox = draw.textbbox((0,0), test_line, font=font)
            w = bbox[2]-bbox[0]
            if w <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    for i, line in enumerate(lines):
        _,h = draw.textbbox((0,0),line,font=font)[2:]
        draw.text((x,y+i*(h+line_spacing)),line,font=font,fill="black")

# Printing schedule to console
def print_schedule(schedule):
    for day in DAYS:
        dayblock = schedule[day]
        total = len(dayblock["Biochem"]) + len(dayblock["Development"]) + len(dayblock["M1"])
        print(f"\n{day} — total topics: {total}")
        print("  Biochem:     ", ", ".join(dayblock["Biochem"]) if dayblock["Biochem"] else "—")
        print("  Development: ", ", ".join(dayblock["Development"]) if dayblock["Development"] else "—")
        print("  M1:          ", ", ".join(dayblock["M1"]) if dayblock["M1"] else "—")

# --- Main ---
if __name__ == "__main__":
    # Debug step
    print("Starting schedule generation... ")
    schedule, counter = generate_schedule()
    # Debug step 2
    print ("Schedule generated. Now printing and validating...")
    print_schedule(schedule)
    validate(schedule, counter)
    draw_calendar_image(schedule)
