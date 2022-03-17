"""A script for gathering stats from ALEKS cohort reports.

The expected format for the report file is a tab-separated text file for which
each student row contains the following columns (starred entries are those that
this script is built to gather):
* 0  - name
  1  - email
  2
  3  - date of last login
  4  - placement assessment number
* 5  - total number of placements taken
  6  - start date
  7  - start time
* 8  - end date
  9  - end time
  10 - proctored assessment
  11 - time in placement
* 12 - placement results
  13 - topics (Whole Numbers, Fractions, and Decimals)
* 14 - result (Whole Numbers, Fractions, and Decimals)
  15 - topics (Percents, Proportions, and Geometry)
* 16 - result (Percents, Proportions, and Geometry)
  17 - topics (Signed Numbers, Linear Equations and Inequalities)
* 18 - result (Signed Numbers, Linear Equations and Inequalities)
  19 - topics (Lines and Systems of Linear Equations)
* 20 - result (Lines and Systems of Linear Equations)
  21 - topics (Relations and Functions)
* 22 - result (Relations and Functions)
  23 - topics (Integer Exponents and Factoring)
* 24 - result (Integer Exponents and Factoring)
  25 - topics (Quadratic and Polynomial Functions)
* 26 - result (Quadratic and Polynomial Functions)
  27 - topics (Rational Expressions and Functions)
* 28 - result (Rational Expressions and Functions)
  29 - topics (Radicals and Rational Exponents)
* 30 - result (Radicals and Rational Exponents)
  31 - topics (Exponentials and Logarithms)
* 32 - result (Exponentials and Logarithms)
  33 - topics (Trigonometry)
* 34 - result (Trigonometry)
* 35 - prep and learning module
* 36 - initial mastery
* 37 - current mastery
  38 - total number of topics learned
  39 - total number of topics learned per hour
  40 - total time in ALEKS prep
* 41 - last math class (level [High School or College])
* 42 - last math class (class)
  43 - last math class (end date)
"""

import numpy as np
import matplotlib.pyplot as plt

#==============================================================================
# Initializing index name lists
#==============================================================================

# Certain text fields in the input file are expected to come from a finite
# list of choices, and are stored in this script's objects as integer IDs.
# The following lists define the meanings for each ID.

# ALEKS module taken
module_dict = {-1: "N/A",
               0: "precalculus",
               1: "calculus"}

# Level of last math class taken
level_dict = {-1: "N/A",
              0: "high school",
              1: "college"}

# Name of last math class taken (collapsed into the following choices)
class_dict = {-1: "N/A",
              0: "other",
              1: "algebra",
              2: "trigonometry",
              3: "geometry",
              4: "precalculus",
              5: "calculus 1",
              6: "calculus 2",
              7: "calculus 3",
              8: "probability/statistics",
              9: "discrete math"}

# ALEKS subject area names, in order
subject_list = ["Whole Numbers, Fractions, and Decimals",                  #  0
                "Percents, Proportions, and Geometry",                     #  1
                "Signed Numbers, Linear Equations and Inequalities",       #  2
                "Lines and Systems of Linear Equations",                   #  3
                "Relations and Functions",                                 #  4
                "Integer Exponents and Factoring",                         #  5
                "Quadratic and Polynomial Functions",                      #  6
                "Rational Expressions and Functions",                      #  7
                "Radicals and Rational Exponents",                         #  8
                "Exponentials and Logarithms",                             #  9
                "Trigonometry"]                                            # 10

#==============================================================================
# Classes (as in objects, not courses)
#==============================================================================

class Student:
    """An object to contain all information from a student's attempts"""

    #--------------------------------------------------------------------------

    def __init__(self, name, cohort=None, module=-1, last_level=-1,
                 last_class=-1):
        """Student(name[, module][, last_level][, last_class])

        Constructs a new student and initializes empty storage attributes.

        Positional arguments:
            name (str) - student name

        Keyword arguments:
            cohort (Cohort) - associated Cohort object
            module (int) - module index (default -1)
            last_level (int) - level of last math class taken (default -1)
            last_class (int) - class ID of last math class taken (default -1)

        This object stores lists of statistics for all attempts. When the main
        CohortReporter object reads a data file, multiple entries for the same
        student are all read into a single object in order to avoid
        overcounting.
        """

        # Initialize attributes
        self.name = name # student name
        self.cohort = cohort # associated cohort object
        self.scores = [] # list of overall scores from all attempts
        self.subject_scores = [] # list of lists of subject scores
        self.module = module # learning modules
        self.masteries = [] # before/after tuples for each module attempt
        self.last_level = last_level # last math class level
        self.last_class = last_class # last math class list index

    #--------------------------------------------------------------------------

    def log_attempt(self, score, subjects, mastery=None):
        """Student.log_attempt(score, subjects[, mastery])

        Adds all data from a given attempt for the student.

        Positional arguments:
            score (int) - overall score for attempt
            subjects (list) - list of subject scores for the attempt

        Keyword arguments:
            mastery (tuple) - before/after mastery level tuple (default None)
        """

        self.scores.append(score)
        self.subject_scores.append(subjects)
        if mastery != None:
            self.masteries.append(mastery)

    #--------------------------------------------------------------------------

    def best_score(self, subjects=False):
        """Student.best_score([subjects])

        Returns the student's best overall score, and optionally subject scores.

        Keyword argument:
            subjects (bool) - True to include a list of subject scores (default
                False)

        Returns:
            (int) - single best score, OR
            (tuple) - single best score and list of corresponding subjects
        """

        if subjects:
            best = self.scores.index(max(self.scores))
            return (self.scores[best], self.subject_scores[best])
        else:
            return max(self.scores)
    
    #--------------------------------------------------------------------------

    def last_score(self, subjects=False):
        """Student.last_score([subjects])

        Returns the student's most recent score, and optionally subject scores.

        Keyword argument:
            subjects (bool) - True to include a list of subject scores (default
                False)

        Returns:
            (int) - most recent score, OR
            (tuple) - most recent score and list of corresponding subjects
        """

        if subjects:
            return (self.scores[0], self.subject_scores[0])
        else:
            return self.scores[0]

#==============================================================================

class Cohort:
    """An object for storing all students in a cohort."""

    #--------------------------------------------------------------------------

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

        # Initialize student dictionary, indexed by name
        self.students = {}

    #--------------------------------------------------------------------------

    def __str__(self):
        """str(Cohort)

        Converts cohort into a string in FaYY, SpYY, or SuYY format.
        """

        if self.season == 0:
            return "Su" + str(self.year)
        elif self.season == 1:
            return "Fa" + str(self.year)
        else:
            return "Sp" + str(self.year)

    #--------------------------------------------------------------------------

    def create_student(self, name, module=-1, last_level=-1, last_class=-1):
        """Cohort.create_student(name[, module][, last_level][, last_class])

        Creates a new Student object in this cohort.

        Positional arguments:
            name (str) - name of new student

        Keyword arguments:
            module (int) - module index (default -1)
            last_level (int) - level of last math class taken (default -1)
            last_class (int) - class ID of last math class taken (default -1)
        """

        # Create student object with given arguments and give pointer to self
        self.students[name] = Student(name, cohort=self, module=module,
                                      last_level=last_level,
                                      last_class=last_class)

    #--------------------------------------------------------------------------

    def add_student(self, student):
        """Cohort.add_student(student)

        Adds an existing student to the cohort and links student to self.
        
        Positional arguments:
            student (Student) - student object to add to the cohort
        """

        # Add student to dictionary and give a pointer to self
        self.students[student.name] = student
        student.cohort = self

    #--------------------------------------------------------------------------

    def update_student(self, name, score, subjects, mastery=None):
        """Cohort.update_student(name, score, subjects[, mastery])

        Updates a student to log a new attempt.
        
        Positional arguments:
            name (str) - name of student to update
            score (int) - overall attempt score
            subjects (list) - list of subject attempt scores

        Keyword arguments:
            mastery (tuple) mastery tuple, if applicable (default None)
        """

        # Call student's logging method
        self.students[name].log_attempt(score, subjects, mastery=mastery)

    #--------------------------------------------------------------------------

    def best_scores(self):
        """Cohort.best_scores()

        Returns the best scores of all students in the cohort
        """

        return [s.best_score() for s in self.students]

    #-------------------------------------------------------------------------

    def last_scores(self):
        """Cohort.last_scores()

        Returns the most recent scores of all students in the cohort
        """

        return [s.last_score() for s in self.students]

#==============================================================================

class CohortReporter:
    """A class to store a group of cohorts and generate summary reports.

    Meant for use a a single global object for storing all cohorts with all
    students, and for handling any data processing needed to gather summary
    statistics for all cohorts.
    """

    #--------------------------------------------------------------------------

    def __init__(self, fname=None):
        """AllCohorts([fname])

        Initializes a storage object based on a given input file.

        Keyword arguments:
            fname (str) - file name to read for student/cohort information
                (default None, which initializes an empty container)
        """

        # Initialize cohort dictionary, indexed by (year, season) tuple
        self.cohorts = {}

        # Read given input file
        if fname != None:
            self.read_file(fname)

    #--------------------------------------------------------------------------

    def read_file(self, fname):
        """AllCohorts.read_file(fname)

        Gathers students and cohorts from a given input file.

        Positional arguments:
            fname (str) - file name to read for student/cohort information
        """

        with open(fname, 'r') as f:
            first = True
            for line in f:

                # Skip the first line
                if first:
                    first = False
                    continue

                # Student entries begin with a quotation mark
                if line[0] != '"':
                    continue

                # Gather tab-separated row
                row = line.split('\t')

                # Find cohort, and create a new Cohort if needed
                ys = date_group(row[8]) # (year, season) ID tuple
                if ys not in self.cohorts:
                    self.cohorts[ys] = Cohort(ys[0], ys[1])
                
                # Find student name
                name = row[0]

                # Gather score
                score = int(row[12].replace('%',''))

                # Gather subject score list
                subjects = [int(row[14+2*i].replace('%','')) for i in range(11)]

                # Gather module and masteries
                module = -1 # module ID
                mastery = None # (initial, final) mastery levels
                if len(row[35]) > 1:
                    if "precalculus" in row[35].lower():
                        module = 0
                    elif "calculus" in row[35].lower():
                        module = 1
                    mastery = (int(row[36].replace('%','')),
                               int(row[37].replace('%','')))

                # Gather last class data
                cls = -1 # class ID from subject_list above
                level = -1 # class level ID
                if len(row[41]) > 1:
                    if "high school" in row[41].lower():
                        level = 0
                    elif "college" in row[41].lower():
                        level = 1
                    cls = class_group(row[42])

                # Create new student if needed
                if name not in self.cohorts[ys].students:
                    self.cohorts[ys].create_student(name, module=module,
                                                    last_level=level,
                                                    last_class=cls)

                # Add attempt information to student
                self.cohorts[ys].update_student(name, score, subjects,
                                                    mastery=mastery)

                ###
                print(ys)
                print(name)
                print(score)
                print(subjects)
                print(module_dict[module])
                print(mastery)
                print(level_dict[level])
                print(class_dict[cls])
                print("-"*20)
                print(self.cohorts[ys])
                print(self.cohorts[ys].students[name].scores)
                print(self.cohorts[ys].students[name].subject_scores)
                print(self.cohorts[ys].students[name].masteries)

                break

#==============================================================================
# Functions
#==============================================================================

def date_group(date):
    """date_group(date)
    
    Converts a date string into a year/season ID tuple.
    
    Positional arguments:
        date (str) - date string, in "MM/DD/YYYY" format
    
    Returns:
        (tuple) - tuple with 2-digit year and season ID
            (0 for Su, 1 for Fa, 2 for Sp)

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
        return (y % 100, 0)
    elif m <= 8:
        return (y % 100, 1)
    else:
        return ((y + 1) % 100, 2)

#------------------------------------------------------------------------------

def class_group(cls):
    """class_group(cls)

    Converts a class name into a standardized set of classes.

    Positional arguments:
        cls (str) - class name

    Returns:
        (int) - a standard class ID number (see class_dict above)
    """
    
    if "no data" in cls or len(cls) < 2:
        return -1
    elif "algebra" in cls.lower() and "linear" not in cls.lower():
        return 1
    elif "trigonometry" in cls.lower():
        return 2
    elif "geometry" in cls.lower():
        return 3
    elif "precalculus" in cls.lower():
        return 4
    elif "calculus ii" in cls.lower() or "calculus 2" in cls.lower():
        return 6
    elif "calculus iii" in cls.lower() or "calculus 3" in cls.lower():
        return 7
    elif "calculus" in cls.lower():
        return 5
    elif "statistics" in cls.lower() or "probability" in cls.lower():
        return 8
    elif "discrete" in cls.lower():
        return 9
    else:
        return 0

#==============================================================================
# Main script
#==============================================================================

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

### Gather data from tab-separated file
##data = [] # selected data from each row
##names = {} # dictionary of names and associated name_row indices
##name_rows = [] # lists of rows, indexed by name
##modules = [] # list of module names, indexed by first appearance in file
##classes = [] # list of math classes, indexed by first appearance in file
##with open("data/AllCohorts.txt", 'r') as f:
##    first = True
##    for line in f:
##        
##        # Skip the first line
##        if first:
##            first = False
##            continue
##        
##        # Student entries begin with a quotation mark
##        if line[0] != '"':
##            continue
##        
##        # Gather row from file and initialize new data row
##        row = line.split('\t')
##        drow = [-1 for i in range(21)]
##
##        # Log name and row
##        if row[0] not in names:
##            names[row[0]] = len(data)
##            name_rows.append([len(data)])
##        else:
##
##
##        
##        drow[0] = hash(row[0])
##        if row[0] not in name_rows:
##            name_rows[drow[0]] = [len(data)]
##        else:
##            name_rows[drow[0]].append(len(data))
##
##        # Log any new modules
##        if row[35] != "-" and row[35] not in modules:
##            modules.append(row[35])
##
##        # Log any new classes
##        cls = class_group(row[42])
##        if len(cls) > 0 and cls not in classes:
##            classes.append(cls)
##
##        # Gather placement data
##        drow[1] = int(row[5]) # placements taken
##
##        # Find cohort group
##        dg = date_group(row[8]) # cohort string
##        if dg[:2] == "Su":
##            drow[2] = 0 # season code
##        elif dg[:2] == "Fa":
##            drow[2] = 1
##        else:
##            drow[2] = 2
##        drow[3] = int(dg[2:]) # 2-digit year
##
##        # Gather placement results
##        for i in range(12):
##            drow[4+i] = int(row[12+2*i].replace('%',''))
##
##        # Gather module index and mastery level (unless module is "-")
##        if row[35] != "-":
##            drow[16] = modules.index(row[35]) # module index
##            drow[17] = int(row[36].replace('%','')) # initial mastery
##            drow[18] = int(row[37].replace('%','')) # current mastery
##
##        # Gather last math class level
##        if row[41].lower() == "high school":
##            drow[19] = 0
##        elif row[41].lower() == "college":
##            drow[19] = 1
##
##        # Gather last math class index (unless unknown)
##        if len(cls) > 0:
##            drow[20] = classes.index(cls)
##
##        # Add new data row
##        data.append(drow)
##
#####
##for i in range(5):
##    print(data[i])
##print("...")
##for i in range(5, 0, -1):
##    print(data[-i])
##print(modules)
##print(classes)
##
##### Find first name with multiple attempts
##nm = 0
##for i in range(len(data)):
##    if len(name_rows[data[i][0]]) > 1:
##        nm = data[i][0]
##        break
##print(name_rows[nm])

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

report = CohortReporter("data/AllCohorts.txt")
print(report.cohorts.keys())

### Stats to try gathering:
# Trends in each score category over time (box and whisker over time?)
# Clustering groups of similar students that span multiple terms (for later A/B testing)
### (after we have result data we can try correlating placements with outcomes)
# Before/after mastery levels for each type of learning module
# See if self-reported last class correlates to performance
