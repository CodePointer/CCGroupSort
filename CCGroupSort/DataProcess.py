# encoding: gbk

from pandas import read_excel, isnull
from xlsxwriter import Workbook


def read_data(file_name):
	"""Read file data from xlsx file"""
	raw_data = read_excel(file_name, sheetname="RawData")
	key_data = raw_data[["身份", "姓名", "一", "二", "三", "四", "五", "六", "日"]]
	return raw_data, key_data


def add_other_data(raw_data, pro_data):
	"""Add other information in raw_data into result_data"""

	# Add cols in pro_data
	new_data = raw_data.copy()
	zero_list = [0] * len(raw_data.index)
	new_data.insert(0, '组别', zero_list)
	new_data.insert(0, '冲突', zero_list)

	# Fill the cols
	for person_idx in raw_data.index:
		new_data.ix[person_idx, '冲突'] = pro_data.ix[person_idx, '冲突']
		new_data.ix[person_idx, '组别'] = pro_data.ix[person_idx, '组别']

	return new_data


def write_data(file_name, res_data, classify=False):
	"""Write data into xlsx file"""
	# 好像openpyxl有点问题
	# print(openpyxl.__version__)
	# writer = ExcelWriter(file_name)
	# res_data.to_excel(writer, sheet_name="ProData")
	# writer.save()
	
	excel_book = Workbook(file_name)
	excel_sheet = excel_book.add_worksheet(u'ResData')
	for i in range(0, len(res_data.columns)):
		excel_sheet.write(0, i, res_data.columns[i])
	for i in res_data.index:
		for j in range(0, len(res_data.columns)):
			# print("iloc[%d][%d]=%s"%(i,j,res_data.iloc[i][j]))
			if not isnull(res_data.iloc[i,j]):
				tmp = res_data.iloc[i,j]
				excel_sheet.write(i+1, j, tmp)
	
	# 分组输出
	if classify:
		groups = set(res_data['组别'])
		for group_num in groups:
			group_data = res_data[res_data['组别'] == group_num]
			if group_num == 0:
				group_name = "无组别(0)"
			else:
				coach_name = list(group_data[group_data['身份'] == '教练']['姓名'])
				group_name = coach_name[0] + '组(%d)' % group_num
			group_sheet = excel_book.add_worksheet(group_name)
			for i in range(0, len(group_data.columns)):
				group_sheet.write(0, i, group_data.columns[i])
			for i in range(0, len(group_data.index)):
				for j in range(0, len(group_data.columns)):
					if not isnull(group_data.iloc[i,j]):
						tmp = group_data.iloc[i,j]
						group_sheet.write(i+1, j, tmp)

	excel_book.close()
	return
