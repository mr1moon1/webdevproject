from bs4 import BeautifulSoup
import requests
import pandas as pd
import re


def ensure_string_columns(df):
	newcols = []
	for col in df.columns:
		strcol = str(col)
		if strcol[0]=="(": #if it's a tuple, instead of a string
			a = strcol
			b = a[a.find("("):a.find(",")]
			c = b[1:]
			d = c.replace("'","")
			strcol = d
		newcols.append(strcol)
	df.columns = newcols
	return df
	
	
# Takes in a pd.df, and returns a clean version of it.
'''
Clean means:
//- There's no nulls where there needs to be a thing.
- There's nothing where the first two attributes are equal (because in that case, they're all probably equal, and this whole row probably isn't mean to be interpreted by the human reader as a thing.
- column names are simple.
'''
def clean(df):
	df = ensure_string_columns(df) #might be inefficient (setting df.columns= multiple times via different function calls), but not a primary concern for now
	columns = df.columns
	
	#Remove all the citation brackets from the Wikipedia:
	for col in columns:
		df[col] =  [re.sub(r'[\(\[].*?[\)\]]','', str(x)) for x in df[col]]
		
	#Remove all the ones where the label is the same throughout the row:
	indexes = []
	for index, row in df.iterrows():
		if row[columns[0]]==row[columns[1]]:
			indexes.append(index)
	for i in indexes:
		df.drop(i, inplace=True)
	
	return df
	
	
	
# Returns a pd.df of the Wiki table, in its original state
def get_original_df(url, tablename):
	response = requests.get(url)
	text = response.text
	following_tablename = text[text.find(tablename):]
	
	soup = BeautifulSoup(following_tablename, "html.parser")
	tables = soup.findAll('table')
	table = tables[0]
	
	listy = pd.read_html(str(table))
	#df = pd.DataFrame(data=listy)
	df = pd.DataFrame(listy[0])
	df = df #idk the exact mechanics of why this is necessary, but it's part of the process.
	
	df = ensure_string_columns(df)
	df = clean(df)
	
	return df
	
	


# Returns the Wiki table, but in an Artifact-friendly format. Also, the return type is a DataFrame.
def wiki2artifacts(url, tablename="", topic=None):
	df = get_original_df(url, tablename)
	cols = df.columns
	print("_________")
	print(cols)

	indices = [i for i, s in enumerate(cols) if (('date' in s) or ('Date' in s))]
	dateindex = indices[0]

	# Get range of indices that don't include 0 or dateindex:
	indices = []
	for i in range(len(cols)):
		indices.append(i)
	indices.remove(indices[dateindex])
	indices.remove(indices[0])

	#Make new df that's good for html
	a = pd.DataFrame()
	a['title'] = df[cols[0]]
	a['date'] = df[cols[dateindex]]
	a['description'] = ""
	for i in indices:
		a['description'] += cols[i]+": "+df[cols[i]]+'\n'
	a['url'] = url
	a['atopic'] = topic #idk if i'll assign topics into SQLAlchemy this way, but it's worth coding this in it seems.
	
	return a