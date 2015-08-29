import copy

class Clause:

	def __init__(self, content, parent_list):
		self.content = content
		self.parent_list = copy.deepcopy(parent_list)

class Task:

	def __init__(self, clause_list):
		self.clause_list = copy.deepcopy(clause_list)

class TaskSolver:

	def __init__(self, task):
		self.clause_list = copy.deepcopy(task.clause_list)

	def solve(self):

		solution_found = False
		addition_to_clause_list = []
		global_index = 0
		length = len(self.clause_list)

		while True:
			for clause1 in self.clause_list:
				if len(self.clause_list) == length:
					global_index += 1
				for clause2 in self.clause_list[global_index:]:
					if clause1.content != clause2.content:
						total_dic = {}
						dic = {}
						parent_list = [clause1, clause2]
						temp_cl1 = copy.deepcopy(clause1.content)
						temp_cl2 = copy.deepcopy(clause2.content)
						for item in temp_cl1:
							for item2 in temp_cl2:
								unify(item, item2, dic, item, item2)
								total_dic.update(dic)
						apply(total_dic, temp_cl1)
						apply(total_dic, temp_cl2)
						result = resolve(temp_cl1, temp_cl2)
						if result == 'empty_clause':
							new_clause = Clause(result, parent_list)
							self.clause_list.append(new_clause)
							solution_found = True
							break
						elif result == None:
							pass
						else:
							found = False
							for clause in self.clause_list:
								if clause.content == result:
									found = True
							for clause in addition_to_clause_list:
								if clause.content == result:
									found = True
							if not found:
								new_clause = Clause(result, parent_list)
								addition_to_clause_list.append(new_clause)
				if solution_found:
						break

			if solution_found:
				break
			if len(addition_to_clause_list) == 0:
				break
			else:
				global_index = len(self.clause_list)
				self.clause_list = self.clause_list + addition_to_clause_list
				subsumption(self.clause_list)
				addition_to_clause_list = []

		if solution_found:
			return self.prettyPrint(new_clause)
		else:
			return ["no"]
		
	def prettyPrint(self, clause):
		print_list = [clause]
		result_list = []
		while len(print_list)>0:
			if len(print_list[0].parent_list)>0:
				result_list.append(self.list_to_str(print_list[0].content))
				result_list.append(self.list_to_str(print_list[0].parent_list[0].content))
				result_list.append(self.list_to_str(print_list[0].parent_list[1].content))
				print_list.append(print_list[0].parent_list[1])
				print_list.append(print_list[0].parent_list[0])
			del print_list[0]
		return result_list

	def list_to_str(self,clause):
		result = ''
		extra = ''
		prefix = ''
		for character in str(clause):
			if character == '[':
				extra = '('
			elif character == '~':
				prefix += character
			elif character == ']':
				result += ')'
			elif character == "'" or character == ' ':
				continue
			elif character == ',':
				if result[-1] != '(':
					result += ','
			else:
				result += prefix+character+extra
				extra = ''
				prefix = ''

		while result.count('(')!=result.count(')'):
			result =  result[:-1] + ""
		return result




# ------------------------------- UNIFICATION -----------------------------------------------------

def is_variable(term, term_list):

	if len(term_list)>0:
		for i in range(len(term_list)):
			if isinstance(term_list[i], str):
				if term_list[i] == term:
					if i==0:
						return False
					else:
						return True
			else:
				return is_variable(term, term_list[i]) + is_variable(term, term_list[i+1:])

	return False


def apply(term_dict, changed_term):

	if len(term_dict)>0:
		for i in range(len(changed_term)):
			if isinstance(changed_term[i], str):
				while changed_term[i] in term_dict.keys():
					for key in term_dict:
						if changed_term[i] == key:
							changed_term[i] = term_dict[key]
	 		else:
	 			apply(term_dict, changed_term[i])


def unify(e1, e2, dict_list, variable_list, variable_list_two):

	if e1 != [] and e2 == []:
		return 'FAIL'
	elif e2 != [] and e1 == []:
		return 'FAIL'

	if not isinstance(e1,list) or not isinstance(e2,list):
		if e1==e2:
			return []
		elif not isinstance(e1,list) and not isinstance(e2,list) and e1.isupper() and e2.isupper() :
			if e1==e2:
				return []
			else:
				return 'FAIL'
		elif not isinstance(e1, list) and e1.islower() and is_variable(e1, variable_list)>0:

			if not isinstance(e2, list):
				return dict_list.update({e1: e2})
			else:
				if e1 in e2:
					return 'FAIL'
				else:
					return dict_list.update({e1: e2})
		elif not isinstance(e2, list) and e2.islower() and is_variable(e2, variable_list_two)>0:
			if not isinstance(e1, list):
				return dict_list.update({e2: e1})
			else:
				if e2 in e1:
					return 'FAIL'
				else:
					return dict_list.update({e2: e1})

		elif isinstance(e1, str) and isinstance(e2, str) and not is_variable(e1, variable_list) and not is_variable(e2, variable_list_two):
			return []

		return 'FAIL'

	if e1==[] and e2==[]:
		return []

	if (len(e1)>0 and len(e2)>0):
		first_e1 = e1[0]
		rest_e1 = e1[1:]
		first_e2 = e2[0]
		rest_e2 = e2[1:]

		z1 = unify(first_e1, first_e2, dict_list, variable_list, variable_list_two)

		if z1=='FAIL':
			return 'FAIL'

		g1 = apply(dict_list, rest_e1)
		g2 = apply(dict_list, rest_e2)

		z2 = unify(rest_e1, rest_e2, dict_list, variable_list, variable_list_two)

		if z2=='FAIL':
			return 'FAIL'

		return [z1 , z2]
	return 'FAIL'


# -------------------------------- RESOLUTION ---------------------------------------------------

def negate(term):
	if term.count('~')%2 == 0:
		return '~' + term[-1]
	else:
		return term[-1]


def resolve(clause1, clause2):

	content = clause1 + clause2

	for item in content:
		if content.count(item)>1:
			content.remove(item)

	content_len = len([item for item in content if content.count(item) == 1])

	for element in content:
		for element2 in content:
			if [negate(element[0])] + element[1:] == element2 or [negate(element2[0])] + element2[1:] == element:
				content.remove(element)
				content.remove(element2)
			elif element == element2:
				continue

	if len(content) == 0:
		return 'empty_clause'
	if len(content) < content_len:
		return content
	else:
		return None

def all_constant(clause):
	if len(clause)>0:
		for i in range(len(clause)):
			if isinstance(clause[i], str):
				if clause[i].islower():
					if i==0:
						continue
					else:
						return True
			else:
				return all_constant(clause[i]) + all_constant(clause[i+1:])

	return False

def function_names(clause):
	
	result = []
	previous = False
	prefix = ''
	for character in str(clause):
		if character=='[':
			previous = True
		else:
			if character == "'":
				continue
			if character == '~':
				prefix = prefix + '~'
				continue
			elif previous:
				result.append(prefix+character)
				previous = False
	return result

def subsumption(clause_list):

	for clause1 in clause_list:
		for clause2 in clause_list:
			if clause1.content != clause2.content:
				if all_constant(clause1.content) == 0 and all_constant(clause2.content) != 0 and function_names(clause1.content) == function_names(clause2.content):
					clause_list.remove(clause1)
				elif all_constant(clause2.content) == 0 and all_constant(clause1.content) != 0 and function_names(clause1.content) == function_names(clause2.content):
					clause_list.remove(clause2)


# ------------------------- INPUT READ HELPERS ---------------------------------------------------------

def create_clause_list(so_far, from_now_on, is_negative):

	if len(from_now_on)>0:
		char=from_now_on[0]
	else:
		return so_far

	if char=='~':
		return create_clause_list(so_far, from_now_on[1:], not is_negative)
	if char.isalpha():
		tomatoes=from_now_on
		rest=[]
		for i in range(len(from_now_on)):
			if not from_now_on[i].isalpha():
				tomatoes = str(from_now_on[:i])
				rest=from_now_on[i:]
				break
		
		if is_negative:
			return create_clause_list(so_far+['~' + tomatoes], rest, False)
		else:
			return create_clause_list(so_far+[tomatoes], rest, is_negative)
	elif char=='(':
		so_far = so_far[:-1] + [[so_far[-1]]+create_clause_list([], from_now_on[1:], is_negative)]
		countpar = 0
		from_now_on = from_now_on[1:]
		while True:
			x = from_now_on[0]
			if x == '(':
				countpar += 1
			elif x == ')' and countpar == 0:
				break
			elif x == ')':
				countpar -= 1
			from_now_on = from_now_on[1:]

		return create_clause_list(so_far, from_now_on[1:], is_negative)
	elif char==')':
		return so_far 		
	elif char==',':
		return  so_far+create_clause_list([], from_now_on[1:], is_negative)	


# -------------------------- MAIN -------------------------------------------------------
if __name__ == "__main__":

	# ----------------- INPUT READ START ------------------------------------

	file = open("input.txt", "r")

	tasks = []
	num_tasks = int(file.readline().strip("\n"))

	while num_tasks > 0:
		num_list = file.readline().strip("\n").split()
		num_base_clauses = int(num_list[0])
		num_obtained_clauses = int(num_list[1])
		clause_list = []
		while num_base_clauses > 0:
			base_clause = file.readline().strip("\n").replace("\t", "").replace(" ","")
			num_base_clauses -= 1;
			clause_content = create_clause_list([],base_clause,False)
			clause = Clause(clause_content, [])
			clause_list.append(clause)
		while num_obtained_clauses > 0:
			obtained_clause = file.readline().strip("\n").replace("\t", "").replace(" ","")
			num_obtained_clauses -= 1;
			clause_content = create_clause_list([],obtained_clause,False)
			clause = Clause(clause_content, [])
			clause_list.append(clause)
		num_tasks -= 1;
		task = Task(clause_list)
		tasks.append(task)

	# ----------------- INPUT READ END ------------------------------------------

	output_file = open("output.txt", 'w')
	for task in tasks:
		solver = TaskSolver(task)
		result = solver.solve()
		index = len(result)
		if index>1:
			output_file.write('yes\n')
			while index>0:
				output_file.write(result[index-2] + '$' + result[index-1] + '$' + result[index-3]+'\n')
				index-=3 
		else:
			output_file.write('no\n')
	output_file.close()


