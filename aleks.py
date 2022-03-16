"""A script for gathering stats from ALEKS cohort reports."""

import numpy as np
import matplotlib.pyplot as plt

#=============================================================================
# Classes (as in objects, not courses)
#=============================================================================

class Student:
    """An object to contain all information from a student's attempts"""

    #-------------------------------------------------------------------------

    def __init__(self, name, module=-1, last_level=-1, last_class=-1):
        """Student(name[, module][, last_level][, last_class])

        Constructs a new student and initializes empty storage attributes.

        Positional arguments:
            name (str) - student name

        Keyword arguments:
            module (int) - module index (default -1)
                -1 for N/A
                0 for precalculus
                1 for calculus
            last_level (int) - level of last math class taken (default -1)
                -1 for unknown
                0 for high school
                1 for college
            last_class (int) - class ID of last math class taken (default -1)
                -1 for unknown
                additional integer IDs defined by global class list
        """

        # Initialize attributes
        self.name = name # student name
        self.cohort = None # associated cohort object (set by cohort)
        self.scores = [] # list of overall scores from all attempts
        self.subject_scores = [] # list of lists of subject scores
        self.module = module # learning module
        self.masteries = [] # before/after tuples for each module attempt
        self.last_level = last_level # last math class level
        self.last_class = last_class # last math class list index

    #-------------------------------------------------------------------------

    def log_attempt(self, row):
        """Student.log_attempt(row)

        Adds all data from a given attempt for the student.

        Positional arguments:
            row (list) - list of attempt attributes, including:
                0 - overall score
                1 - whole numbers, fractions, and decimals
                2 - percents, proportions, and geometry
                3 - signed numbers, linear equations, and inequalities
                4 - lines and systems of linear equations
                5 - relations and functions
                6 - integer exponents and factoring
                7 - quadratic and polynomial functions
                8 - rational expressions and functions
                9 - radicals and rational exponents
                10 - exponents and logarithms
                11 - trigonometry
                12 - "before" module mastery
                13 - "after" module mastery
        """

        self.scores.append(row[0])
        self.subject_scores.append(row[1:12])
        self.masteries.append(tuple(row[12:14]))

    #---------------------------------------------------------------------

    def best_score(self):
        """Student.best_score()

        Returns the student's best overall score.
        """

        return max(self.scores)
    
    #---------------------------------------------------------------------

    def last_score(self):
        """Student.last_score()

        Returns the student's most recent overall score.
        """

        return self.scores[0]

#=============================================================================

class Cohort:
    """An object for storing all students in a cohort."""

    #-------------------------------------------------------------------------

    def __init__(self, year, season):
        """Cohort(year, season)

        Initializes a new cohort.

        Positional arguments:
            year (int) - 2-digit cohort year
            season (int) - season ID (0 Su, 1 Fa, 2 Sp)
        """

        # Initialize attributes
        self.year = year
        self.season = season

        # Initialize student list
        self.students = []

    #-------------------------------------------------------------------------

    def __str__(self):
        """str(Cohort)

        Converts cohort into a string in FaYY, SpYY, or SuYY format.
        """

        if season == 0:
            return "Su" + str(year)
        elif season == 1:
            return "Fa" + str(year)
        else:
            return "Sp" + str(year)

    #-------------------------------------------------------------------------

    def add_student(self, student):
        """Cohort.add_student(student)

        Adds a student to the cohort and gives the student a pointer to it.

        Positional arguments:
            student (Student) - student object to add to the cohort
        """

        # Add student to list and give a pointer to self
        self.students.append(student)
        student.cohort = self

    #-------------------------------------------------------------------------

    def best_scores(self):
        """Cohort.best_score()

        Returns the best scores of all students in the cohort
        """

        return [s.best_score() for s in self.students]

    #-------------------------------------------------------------------------

    def last_scores(self):
        """Cohort.last_score()

        Returns the most recent scores of all students in the cohort
        """

        return [s.last_score() for s in self.students]

#=============================================================================
# General Functions
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

    if "no data" in cls or len(cls) < 2:
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
# Filtering Functions
#=============================================================================

### Select by last class, with option for most recent only or best only

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
# 0  - (int) name index (from "names" list)
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
names = {} # dictionary of names and associated name_row indices
name_rows = [] # lists of rows, indexed by name
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

        # Log name and row
        if row[0] not in names:
            names[row[0]] = len(data)
            name_rows.append([len(data)])
        else:


        
        drow[0] = hash(row[0])
        if row[0] not in name_rows:
            name_rows[drow[0]] = [len(data)]
        else:
            name_rows[drow[0]].append(len(data))

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

### Find first name with multiple attempts
nm = 0
for i in range(len(data)):
    if len(name_rows[data[i][0]]) > 1:
        nm = data[i][0]
        break
print(name_rows[nm])

### Count cohorts
### Note: This inclues *all* exams, which is overcounting due to retakes
### This can maybe be solved by filtering 
##for ch in [(0, 17), (1, 17), (2, 17), (0, 18), (1, 18), (2, 18),
##           (0, 19), (1, 19), (2, 19), (0, 20), (1, 20), (2, 20),
##           (0, 21), (1, 21), (2, 21), (0, 22), (1, 22), (2, 22)]:
##    tot = 0
##    for i in range(len(data)):
##        if data[i][2] == ch[0] and data[i][3] == ch[1]:
##            tot += 1
##    print(str(ch) + '\t' + str(tot))

### Stats to try gathering:
# Trends in each score category over time (box and whisker over time?)
# Clustering groups of similar students that span multiple terms (for later A/B testing)
### (after we have result data we can try correlating placements with outcomes)
# Before/after mastery levels for each type of learning module
# See if self-reported last class correlates to performance
