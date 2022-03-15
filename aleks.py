"""A script for gathering stats from ALEKS cohort reports."""

# Column indices are as follows:
# * 0  - name (gather as a hash to anonymize)
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
# * 43 - last math class (end date)

# Gather data from tab-separated file
rows = [] # full data from each row, indexed as above
names = {} # lists of rows, indexed by name hash
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
        
        # Gather tab-separated row
        rows.append(line.split('\t'))

        # Hash name to anonymize, then log rows
        rows[-1][0] = hash(rows[-1][0])
        if rows[-1][0] not in names:
            names[rows[-1][0]] = [len(rows)]
        else:
            names[rows[-1][0]].append(len(rows))

### Stats to try gathering:
# Trends in each score category over time (requires grouping students by term; just make box and whisker charts to get an idea)
# Clustering groups of similar students that span multiple terms (for later A/B testing)
### (after we have result data we can try correlating placements with outcomes)
