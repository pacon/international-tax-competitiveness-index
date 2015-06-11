#
# International Tax Competitiveness Index - Python edition
#
# Patrick Conheady, June 2015
#
# The Tax Foundation has not endorsed this at all. This is an
# exercise in studying the ITCI and learning to use Python/PANDAS.
# My script calculates the same scores and ranks as those that appear
# in the Tax Foundation's PDF report on the ITCI. 
#

import numpy as np
import pandas as pd
import scipy.stats as st

# Read variable scores from database
d = pd.read_csv('indexdata.csv')
d = d.set_index('country')

# Standardise the variable scores
# i.e. (x - mean) / std
z = (d - d.mean()) / d.std()

# Flip variables which are 'bad' to be large.
# 
# Note we stuff around with column numbers and names because the documentation 
# (in Tax Foundation's R script) refers to column names which differ from those
# in the CSV. The easiest way to copy the list of columns from the R script is
# by taking the numeric list, which is 1-based and includes 'country' as #1.
cols = ['']
cols.append(d.index.name)
for x in d.columns.values:
    cols.append(x)
vars_to_flip = []
# The following list of column numbers copied from Tax Foundation's R script.
for x in (2,9,10,11,12,13,14,15,17,18,19,20,21,22,23,24,25,26,27,29,30,31,32,33,34,37,38,39,41,42,43):
    vars_to_flip.append(cols[x])
for x in vars_to_flip:
    z[x] = -z[x]

#
# Categories and subcategories
# The indexes/ranges within `cols` are copied from the Tax Foundation's R script.
# The "+1" is because R and Python slice differently.
#
categories = {
    'Corporate tax': {
            'Rate': cols[2:2+1],
            'Cost recovery': cols[3:8+1],
            'Incentives/complexity': cols[9:13+1],
        },
    'Consumption taxes': {
            'Rate': cols[14:14+1],
            'Base':  cols[15:17+1],
            'Complexity': cols[18:18+1]
        },
    'Property taxes': {
            'Real property taxes': cols[19:20+1],
            'Wealth/estate taxes':  cols[21:22+1],
            'Capital/transaction taxes':cols[23:26+1]
        },
    'Individual taxes': {
            'Capital gains/dividends': cols[27:29+1],
            'Income tax': cols[30:32+1],
            'Complexity': cols[33:34+1]
        },
    'International tax rules': {
            'Div/cap gains exemption (territoriality)': cols[35:36+1],
            'Withholding taxes':cols[37:40+1],
            'Regulations': cols[41:43+1]
        }
    }
# Code to print the category hierarchy with column names:
#for cat in categories:
#    print cat
#    for sub in categories[cat]:
#        print '   ' + sub
#        for col in categories[cat][sub]:
#            print '   ' + '   ' + col

#
# Add up subcategory and category scores
#
scores = pd.DataFrame(index=d.index)

scores['Overall score'] = 0.0

for cat in categories:
    scores[cat] = 0.0
    for sub in categories[cat]:
        scores[cat + ' - ' + sub] = 0.0
        for col in categories[cat][sub]:
            scores[cat + ' - ' + sub] += 1.0/len(categories[cat][sub]) * z[col]
        scores[cat] += 1.0/len(categories[cat]) * scores[cat + ' - ' + sub]
    scores['Overall score'] += 1.0/len(categories) * scores[cat]

def pnorm_scale_to(x, index, to=100):
    # Apparently R's pnorm() is best represented by SciPy's cdf()
    # See http://adorio-research.org/wordpress/?p=284
    p = st.norm.cdf(x)
    return pd.Series(p, index=index)/float(max(p))*to

# Create a copy of the scores table, convert to p-values and scale to 100.
scores_final = pd.DataFrame(index=d.index)
scores_final = scores.copy()
for col in scores_final.columns.values:
    scores_final[col] = pnorm_scale_to(scores_final[col], scores_final.index, 100)

# Add ranks
for col in scores_final.columns.values:
    scores_final[str(col) + ' - Rank'] = scores_final[col].rank(ascending=False, method='min')

# Round to one decimal place to look like ITCI report.
scores_final = scores_final.apply(lambda x: np.round(x, decimals=1))
	
# Done
print scores_final
