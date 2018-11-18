import os
import re

# increment .sql files changed
changes = 0

fix = {
	"keywords": {
		"select": "SELECT",
		"distinct": "DISTINCT",
		"case": "CASE",
		"when": "WHEN",
		"then": "THEN",
		"end": "END",
		"else": "ELSE",
		"from": "FROM",
		"as": "AS",
		"left": "LEFT",
		"inner": "INNER",
		"right": "RIGHT",
		"join": "JOIN",
		"union": "UNION",
		"where": "WHERE",
		"and": "AND",
		"or": "OR",
		"not": "NOT",
		"on": "ON",
		"in": "IN",
		"is": "IS",
		"if": "IF",
		"using": "USING",
		"like": "LIKE",
		"group": "GROUP",
		"order": "ORDER",
		"by": "BY",
		"desc": "DESC",
		"asc": "ASC"
	},
	"substrings": {
		"date_format": "DATE_FORMAT",
		"coalesce": "COALESCE",
		"curdate": "CURDATE",
		"concat": "CONCAT",
		"ifnull": "IFNULL",
		"count": "COUNT",
		"round": "ROUND",
		"sum": "SUM",
		"avg": "AVG",
		"min": "MIN",
		"max": "MAX",
		"nvl": "NVL",
		"if": "IF"
	},
	"operators": [
		">=",
		"<=",
		"<>",
		">",
		"<",
		"=",
		"+",
		"-",
		"/",
		"*",
		","
	]
}

# check if operator index is odd when sorted into quote list
def check_indexes(index_list, operator_index):
	index_list.append(operator_index)
	index_list.sort()
	return index_list.index(operator_index) % 2 == 0

# checks operator spacing
def check_operators(line):
	for operator in fix["operators"]:
		if operator in line:
			single_indexes = []
			double_indexes = []
			single = re.finditer("'", line)
			double = re.finditer('"', line)
			for index in single: single_indexes.append(index.start())
			for index in double: double_indexes.append(index.start())
			if (check_indexes(single_indexes, line.index(operator)) and
					check_indexes(double_indexes, line.index(operator)) and
					(line.index(operator) == 0 or line[line.index(operator) - 1] not in fix["operators"]) and
					(line.index(operator) == len(line) - 1 or line[line.index(operator) + 1] not in fix["operators"])):
				line = line.replace(operator, " {} ".format(operator) if operator != "," else "{} ".format(operator))
	return line

def sql_writer(file_name):
	global changes
	print file_name
	sql_read = open(file_name, 'r')
	sql = sql_read.read()
	sql_read.close()
	sql = sql.split("\n")
	change = 0

	for ind, line in enumerate(sql):
		# extract leading whitespace
		prepend = line[:-len(line.lstrip())]

		line = check_operators(line)
		line = line.split()

		for index, word in enumerate(line):
			if word in fix["keywords"]:
				line[index] = fix["keywords"][word]
				change += 1
			else:
				word = word.split("(")
				for i, w in enumerate(word):
					for key, value in fix["substrings"].iteritems():
						if key in w:
							word[i] = w.replace(key, value)
							change += 1
				word = "(".join(word)
				line[index] = word
		
		line = " ".join(line)
		
		if ("GROUP BY" in line or "ORDER BY" in line or "SELECT" in line) and line.count(",") > 1:
			line = line.replace(",", ",\n   ")
			if line[-5:] == ",\n   ": line = line[:-4] 
		sql[ind] = prepend + line

	sql = "\n".join(sql)

	print "{} change{}".format(change, "s" if change is not 1 else "")
	if change > 0: changes += 1

	text_file = open(file_name, "w")
	text_file.write(sql)
	text_file.close()

for file in os.listdir("."):
    if file.endswith(".sql"): 
        sql_writer(file)

print "{} .sql files altered.".format(changes)
