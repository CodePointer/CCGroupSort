# encoding: gbk

from math import ceil
from pandas import DataFrame, Series

MAX_INDEX = 2048
MAX_STUDENT_NUM = 2048


class Node(object):
	"""Node class of network flow"""

	_total_num = 0

	def __init__(self, data=""):
		"""Initialize"""

		Node._total_num += 1
		self._index = Node._total_num
		if type(data) == str:
			self._name = data
			self._identity = ""
		else:
			self._name = data['姓名']
			self._identity = data['身份']
			self._time = list(data['一':'日'])
			for idx in range(0, len(self._time)):
				if self._time[idx] != 1:
					self._time[idx] = 0
			self._group = -1
		self.edges = {}
		self.reverse_edges = {}

		return

	def create_edge(self, end_node, max_flow=1.0):
		"""Create network, left_network for graph creating"""

		self.edges[end_node.get_index()] = [0, max_flow]
		self.reverse_edges[end_node.get_index()] = max_flow

		return True

	def update_edge(self, end_node, add_flow):
		"""Update an edge in the network flow; Update the left_network in the same time"""
		# print("Update.Before: %d" % addFlow)
		# print(self.edges)
		# print(self.redges)
		# if endNode.index == 69:
		# print("self: ", self.name, " ", self.iden, " ", self.index)
		# print(self.edges)
		# print("endNode: ", endNode.name, " ", endNode.iden, " ", endNode.index)

		if end_node.get_index() not in self.edges:
			end_node.update_edge(self, -add_flow)
			return
		else:
			if self.edges[end_node.get_index()][0] + add_flow > self.edges[end_node.get_index()][1]:
				return False
			else:
				max_flow = self.edges[end_node.get_index()][1]
				self.edges[end_node.get_index()][0] += add_flow
				self.reverse_edges[end_node.get_index()] = max_flow - self.edges[end_node.get_index()][0]
				end_node.reverse_edges[self._index] = self.edges[end_node.get_index()][0]
		# print("After:")
		# print(self.edges)
		# print(self.redges)
		return

	def search_group(self, group_table):
		"""Set self._group"""

		if self._identity == "教练":
			self._group = group_table[self._index]
		elif self._identity == "学员":
			# print(self.edges)
			for idx in self.edges:
				value = self.edges[idx][0]
				if value != 0:
					res_idx = idx
					break
			else:
				res_idx = -1
			self._group = group_table[res_idx]
		else:  # Sourse and terminal，set to 0
			self._group = 0

		return

	def get_identity(self):
		"""Get node's identity"""
		return self._identity

	def get_time(self):
		"""Get node's time"""
		return self._time

	def get_index(self):
		"""Get node's index"""
		return self._index

	def get_group(self):
		"""Get node's group"""
		return self._group

	def get_name(self):
		"""Get node's name"""
		return self._name


def _check_time(node1, node2):
	"""Check node's time is good"""

	node1_time = node1.get_time()
	node1_identity = node1.get_identity()
	node2_time = node2.get_time()
	node2_identity = node2.get_identity()
	if node1_identity == "教练":
		for i in range(0, 6):
			if (node1_time[i] == 1) and (node2_time[i] != 1):
				return False
		else:
			return True
	elif node2_identity == "教练":
		for i in range(0, 6):
			if (node2_time[i] == 1) and (node1_time[i] != 1):
				return False
		else:
			return True
	else:
		return False


def _deep_first_search(node_list, start_node, terminal_node):
	"""dfs to search for augmenting path"""

	# Initialize
	stack = [[[start_node.get_index(), MAX_INDEX], [start_node.get_index()]]]
	total_trace = []
	total_state = []

	while len(stack) > 0:

		# For every state in the stack, check the terminal state
		[state, trace] = stack.pop()
		if state[0] is terminal_node.get_index():
			total_state = state
			total_trace = trace
			break
		# print("Begin. Stack: ",end = "")
		# print(stack)
		# print("\tPop: ",end = "")
		# print([state, trace])

		# Search all the possible edges in node
		for idx in node_list[state[0]].reverse_edges:
			edge_val = node_list[state[0]].reverse_edges[idx]
			# print("NodeList[%d].redges[%d]=%d" % (state[0], idx, edg))
			if (edge_val > 0) and (idx not in trace):  # 还有余量，并且路径不重复
				# Create a new path
				new_state = state.copy()
				new_state[0] = idx
				if state[1] > edge_val:  # 不足以支持原先的流量,下调
					new_state[1] = edge_val
				new_trace = trace.copy()
				new_trace.append(idx)
				stack.append([new_state, new_trace])
			# print("End. Stack: ",end = "")
			# print(stack)
			# system("PAUSE")

	return [total_state, total_trace].copy()


def _my_debug(node_list):
	# Debug: 输出图
	for Idx in node_list:
		print("Name: %s,(%d)" % (node_list[Idx].name, Idx))
		print("Edges: ")
		print(node_list[Idx].edges)
		print("rEdges: ")
		print(node_list[Idx].redges)
		print("")


def main_loop(pro_data, ignore_time):
	"""Main loop of network flow"""

	# 将数据分为教练、学员两类
	# teacherData = proData[proData["身份"]=="教练"]
	# studentData = proData[proData["身份"]=="学员"]

	# Create nodes
	source_node = Node("Source")
	tink_node = Node("Tink")
	node_list = {source_node.get_index(): source_node, tink_node.get_index(): tink_node}
	for idx in pro_data.index:
		temp_node = Node(pro_data.loc[idx])
		node_list[temp_node.get_index()] = temp_node

	# Create edges between nodes
	possible_student = set()
	for Idx in node_list.keys():
		# for every teacher, find the possible student
		if node_list[Idx].get_identity() == "教练":
			for idx in node_list.keys():
				if node_list[idx].get_identity() == "学员":
					# 如果学员和教练时间匹配
					match = _check_time(node_list[Idx], node_list[idx])
					if match:
						node_list[idx].create_edge(node_list[Idx])
						possible_student.add(idx)  # 将学员idx加入集合中，统计总人数
	# print(PossibleStudent)

	# Create edges between nodes and source, tink
	group_num = len(pro_data[pro_data["身份"] == "教练"])
	people_per_group = ceil(len(possible_student) / group_num)
	for Idx in node_list:
		# for every teacher, fix people_per_group into tink
		if node_list[Idx].get_identity() == "教练":
			node_list[Idx].create_edge(node_list[tink_node.get_index()], max_flow=people_per_group)
		# for every student, link source edge to student edge
		elif (node_list[Idx].get_identity() == "学员") and (Idx in possible_student):
			node_list[source_node.get_index()].create_edge(node_list[Idx])
	# Debug(NodeList)
	# system("PAUSE")

	# Main loop
	while True:
		# DFS
		(state, trace) = _deep_first_search(node_list, source_node, tink_node)
		# print("Find a Trace: ",end = "")
		# print(trace)

		# Process trace
		if len(trace) <= 0:
			break
		else:
			start_idx = source_node.get_index()
			for dst in trace[1:]:
				node_list[start_idx].update_edge(node_list[dst], state[1])
				start_idx = dst
			# Debug(NodeList)
			# system("PAUSE")
	# Debug(NodeList)

	# Make group table
	group_cnt = 1
	group_table = {-1: 0}  # 无组别的人，映射至0
	for idx in node_list:
		if node_list[idx].get_identity() == "教练":
			group_table[idx] = group_cnt
			group_cnt += 1
	# print(groupTable)
	for idx in node_list:
		node_list[idx].search_group(group_table)

	# Output data_frame
	col = ['冲突', '组别', '身份', '姓名', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
	result_data = DataFrame([], columns=col)
	for idx in node_list:
		if node_list[idx].get_identity() != "": # is student or teacher
			result_list = [0, node_list[idx].get_group(), node_list[idx].get_identity(), node_list[idx].get_name()] + node_list[idx].get_time()
			result_series = Series(result_list, index=col)
			result_data = result_data.append(result_series, ignore_index=True)

	# Divide group anyway
	if ignore_time:
		no_group_set = result_data[result_data["组别"] == 0].copy()
		teacher_set = result_data[result_data['身份'] == '教练'].copy()

		# Add group information in no_group_set
		for group_idx in range(1, group_cnt):
			no_group_set[group_idx] = 0.0
		no_group_set['2_day_match'] = 0.0
		no_group_set['1_day_match'] = 0.0

		# Check time with teacher_set
		for person_idx in no_group_set.index:
			person_time = list(no_group_set.loc[person_idx]['周一':'周日'])
			day_2_match_num = 0
			day_1_match_num = 0
			for group_idx in range(1, group_cnt):
				teacher_time = list(teacher_set[teacher_set['组别'] == group_idx].iloc[0]['周一':'周日'])
				match_days = 0
				for day_idx in range(0, 7):
					if person_time[day_idx] == 1 and teacher_time[day_idx] == 1:
						match_days += 1
				if match_days == 2:
					day_2_match_num += 1
				elif match_days == 1:
					day_1_match_num += 1
				no_group_set.ix[person_idx, group_idx] = match_days
			no_group_set.ix[person_idx, '2_day_match'] = day_2_match_num
			no_group_set.ix[person_idx, '1_day_match'] = day_1_match_num
		# no_group_set = no_group_set.sort_values(['2_day_match', '1_day_match'], ascending=True)

		# Count student num in every group
		group_student_num = {}
		for group_idx in range(1, group_cnt):
			group_student_num[group_idx] = len(result_data[result_data['组别'] == group_idx])
		# check 2_day avaliable student
		set_2_day = no_group_set[no_group_set['2_day_match'] != 0].sort_values(['2_day_match'], ascending=True)
		for person_idx in set_2_day.index:
			group_match_val = [0] * (group_cnt - 1)
			for group_idx in range(1, group_cnt):
				if no_group_set.loc[person_idx][group_idx] == 2:
					group_match_val[group_idx - 1] = group_student_num[group_idx]
				else:
					group_match_val[group_idx - 1] = MAX_STUDENT_NUM
			in_group = group_match_val.index(min(group_match_val)) + 1
			group_student_num[in_group] += 1
			no_group_set.ix[person_idx, '冲突'] = 0.0
			no_group_set.ix[person_idx, '组别'] = in_group
		# check 1_day avaliable student
		set_1_day = no_group_set[no_group_set['1_day_match'] != 0].sort_values(['1_day_match'], ascending=True)
		for person_idx in set_1_day.index:
			group_match_val = [0] * (group_cnt - 1)
			for group_idx in range(1, group_cnt):
				if no_group_set.loc[person_idx][group_idx] == 1:
					group_match_val[group_idx - 1] = group_student_num[group_idx]
				else:
					group_match_val[group_idx - 1] = MAX_STUDENT_NUM
			in_group = group_match_val.index(min(group_match_val)) + 1
			group_student_num[in_group] += 1
			no_group_set.ix[person_idx, '冲突'] = 1.0
			no_group_set.ix[person_idx, '组别'] = in_group
		# check not avaliable student
		left_set = no_group_set[no_group_set['组别'] == 0]
		for person_idx in left_set.index:
			group_match_val = [0] * (group_cnt - 1)
			for group_idx in range(1, group_cnt):
				group_match_val[group_idx - 1] = group_student_num[group_idx]
			in_group = group_match_val.index(min(group_match_val)) + 1
			group_student_num[in_group] += 1
			no_group_set.ix[person_idx, '冲突'] = 2.0
			no_group_set.ix[person_idx, '组别'] = in_group

		# Add student from no_group_set into result_data
		for person_idx in no_group_set.index:
			result_data.ix[person_idx, '冲突'] = no_group_set.loc[person_idx, '冲突']
			result_data.ix[person_idx, '组别'] = no_group_set.loc[person_idx, '组别']

	result_data = result_data.sort_values(["组别", "身份"], ascending=False)

	return result_data

