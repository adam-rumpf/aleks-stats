"""A script for gathering stats from ALEKS cohort reports."""

#=============================================================================
# Functions
#=============================================================================

#-----------------------------------------------------------------------------
def date_group(date):
    """date_group(date)
    
    Converts a date string into the nearest matching cohort string.
    
    Positional arguments:
        date (str) - date string, in "MM/DD/YYYY" format
    
    Returns:
        (str) - cohort string, in "FaYY", "SpYY", or "SuYY" format

    The cutoffs for Fall, Spring, and Summer are:
        Jan-May: Summer
        June-August: Fall
        September-December: (next) Spring
    """
    
    # Gather month, day, and year
    parts = date.split('/')
    if len(parts) != 3:
        raise ValueError('date string must be in "MM/DD/YYYY" format')
    m = int(parts[0])
    d = int(parts[1])
    y = int(parts[2])
    
    # Use month and day to determine season
    if m <= 5:
        return "Su" + str(y % 100)
    elif m <= 8:
        return "Fa" + str(y % 100)
    else:
        return "Sp" + str((y + 1) % 100)

#-----------------------------------------------------------------------------
def class_group(cls):
    """class_group(cls)

    Converts a class name into a standardized set of classes.

    Positional arguments:
        cls (str) - class name

    Returns:
        (str) - a standard class name, or the empty string if N/A
    """

    if "no data" in cls:
        return ""
    elif "algebra" in cls.lower() and "linear" not in cls.lower():
        return "Algebra"
    elif "trigonometry" in cls.lower():
        return "Trigonometry"
    elif "geometry" in cls.lower():
        return "Geometry"
    elif "precalculus" in cls.lower():
        return "Precalculus"
    elif "calculus ii" in cls.lower() or "calculus 2" in cls.lower():
        return "Calculus II"
    elif "calculus iii" in cls.lower() or "calculus 3" in cls.lower():
        return "Calculus III"
    elif "calculus" in cls.lower():
        return "Calculus I"
    elif "statistics" in cls.lower():
        return "Statistics"
    elif "IB" in cls:
        return "IB Mathematics"
    elif "discrete" in cls.lower():
        return "Discrete Mathematics"
    else:
        return "Other"

#=============================================================================
# Main script
#=============================================================================

# Column indices of the input file are as follows:
# * 0  - name
#   1  - email
#   2
#   3  - date of last login
#   4  - placement assessment number
# * 5  - total number of placements taken
#   6  - start date
#   7  - start time
# * 8  - end date
#   9  - end time
#   10 - proctored assessment
#   11 - time in placement
# * 12 - placement results
#   13 - topics (Whole Numbers, Fractions, and Decimals)
# * 14 - result (Whole Numbers, Fractions, and Decimals)
#   15 - topics (Percents, Proportions, and Geometry)
# * 16 - result (Percents, Proportions, and Geometry)
#   17 - topics (Signed Numbers, Linear Equations and Inequalities)
# * 18 - result (Signed Numbers, Linear Equations and Inequalities)
#   19 - topics (Lines and Systems of Linear Equations)
# * 20 - result (Lines and Systems of Linear Equations)
#   21 - topics (Relations and Functions)
# * 22 - result (Relations and Functions)
#   23 - topics (Integer Exponents and Factoring)
# * 24 - result (Integer Exponents and Factoring)
#   25 - topics (Quadratic and Polynomial Functions)
# * 26 - result (Quadratic and Polynomial Functions)
#   27 - topics (Rational Expressions and Functions)
# * 28 - result (Rational Expressions and Functions)
#   29 - topics (Radicals and Rational Exponents)
# * 30 - result (Radicals and Rational Exponents)
#   31 - topics (Exponentials and Logarithms)
# * 32 - result (Exponentials and Logarithms)
#   33 - topics (Trigonometry)
# * 34 - result (Trigonometry)
# * 35 - prep and learning module
# * 36 - initial mastery
# * 37 - current mastery
#   38 - total number of topics learned
#   39 - total number of topics learned per hour
#   40 - total time in ALEKS prep
# * 41 - last math class (level [High School or College])
# * 42 - last math class (class)
#   43 - last math class (end date)

# Indices of the collected data are as follows:
# 0  - (int) name hash (from "names" dictionary)
# 1  - (int) total number of placements taken
# 2  - (int) cohort season (0 for Su, 1 for Fa, 2 for Sp)
# 3  - (int) cohort year (last two digits only)
# 4  - (int) placement results (0-100)
# 5  - (int) result (Whole Numbers, Fractions, and Decimals)
# 6  - (int) result (Percents, Proportions, and Geometry)
# 7  - (int) result (Signed Numbers, Linear Equations and Inequalities)
# 8  - (int) result (Lines and Systems of Linear Equations)
# 9  - (int) result (Relations and Functions)
# 10 - (int) result (Integer Exponents and Factoring)
# 11 - (int) result (Quadratic and Polynomial Functions)
# 12 - (int) result (Rational Expressions and Functions)
# 13 - (int) result (Radicals and Rational Exponents)
# 14 - (int) result (Exponentials and Logarithms)
# 15 - (int) result (Trigonometry)
# 16 - (int) prep and learning module index (-1 if N/A)
# 17 - (int) initial mastery (-1 if N/A)
# 18 - (int) current mastery (-1 if N/A)
# 19 - (int) last math class (-1 for unknown, 0 for high school, 1 for college)
# 20 - (int) last math class index (-1 if unknown)

# Gather data from tab-separated file
data = [] # selected data from each row
names = {} # lists of rows, indexed by name hash
modules = [] # list of module names, indexed by first appearance in file
classes = [] # list of math classes, indexed by first appearance in file
with open("data/AllCohorts.txt", 'r') as f:
    first = True
    for line in f:
        
        # Skip the first line
        if first:
            first = False
            continue
        
        # Student entries begin with a quotation mark
        if line[0] != '"':
            continue
        
        # Gather row from file and initialize new data row
        row = line.split('\t')
        drow = [-1 for i in range(21)]

        # Hash name to anonymize, then log row
        drow[0] = hash(row[0])
        if row[0] not in names:
            names[row[0]] = [len(data)]
        else:
            names[row[0]].append(len(data))

        # Log any new modules
        if row[35] != "-" and row[35] not in modules:
            modules.append(row[35])

        # Log any new classes
        cls = class_group(row[42])
        if len(cls) > 0 and cls not in classes:
            classes.append(cls)

        # Gather placement data
        drow[1] = int(row[5]) # placements taken

        # Find cohort group
        dg = date_group(row[8]) # cohort string
        if dg[:2] == "Su":
            drow[2] = 0 # season code
        elif dg[:2] == "Fa":
            drow[2] = 1
        else:
            drow[2] = 2
        drow[3] = int(dg[2:]) # 2-digit year

        # Gather placement results
        for i in range(12):
            drow[4+i] = int(row[12+2*i].replace('%',''))

        # Gather module index and mastery level (unless module is "-")
        if row[35] != "-":
            drow[16] = modules.index(row[35]) # module index
            drow[17] = int(row[36].replace('%','')) # initial mastery
            drow[18] = int(row[37].replace('%','')) # current mastery

        # Gather last math class level
        if row[41].lower() == "high school":
            drow[19] = 0
        elif row[41].lower() == "college":
            drow[19] = 1

        # Gather last math class index (unless unknown)
        if len(cls) > 0:
            drow[20] = classes.index(cls)

        # Add new data row
        data.append(drow)

###
for i in range(5):
    print(data[i])
print("...")
for i in range(5, 0, -1):
    print(data[-i])
print(modules)
print(classes)

### Stats to try gathering:
# Trends in each score category over time (requires grouping students by term; just make box and whisker charts to get an idea)
# Clustering groups of similar students that span multiple terms (for later A/B testing)
### (after we have result data we can try correlating placements with outcomes)
# Before/after mastery levels for each type of learning module
