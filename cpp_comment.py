#!/usr/bin/env python
# Copyright (c) 2020 sbyxb.  
#

import codecs
import copy
import getopt
import glob
import itertools
import math
import os
import re
import sre_compile
import string
import sys
import sysconfig
import unicodedata

# if empty, use defaults
_HeaderExtension = {'h', 'hh', 'hpp', 'hxx', 'h++', 'cuh'}
_CppExtension = {'c', 'cc', 'cpp', 'cxx', 'c++', 'cu'}

_list_comment_template = [
"/** @func       ",
" *  @brief      ",
" *  @param      ",
" *  @return     ",
" */"]

_reg_exp_cur = r'\w( +|\W +)\w(\w|::)*\(.*(\)|;)' # function declare
_reg_exp_next = r'\s*{' # check next line have function body
_regexp_bracket = r'\b\(.*\)' # bracket content

def ProcFile(file):
    dict_func_line, read_line_buf = GetFunctionLine(file)
    key_lines = dict_func_line.keys()
    list_lines = list(key_lines)
    list_lines.sort()
    for line_num in reversed(list_lines):
        ProcFuncLine(dict_func_line[line_num], line_num, read_line_buf)

    write_file = open(file + "_comment", "w+", encoding='UTF-8')
    for line_one in read_line_buf:
        write_file.write(line_one)
        write_file.flush()
    write_file.close()

def GetFunctionLine(file):
    read_file = open(file, 'r', encoding='UTF-8')
    read_line_buf = read_file.readlines()
    dict_func_line = {}

    for idx_line in range(1, len(read_line_buf) - 1):
        line_prve = read_line_buf[idx_line - 1]
        line_cur = read_line_buf[idx_line]
        line_next = read_line_buf[idx_line + 1]
        match_cur = False
        if re.search(_reg_exp_cur, line_cur):
            reg_if_else = r'(\bif\b | \belse if\b| \belse\b)'
            if not re.search(reg_if_else, line_cur):
                match_cur = True
        if match_cur:
            print(line_cur)
            if re.search(_reg_exp_next, line_next) or ";" in line_cur or "{" in line_cur:
                dict_func_line[idx_line] = (line_prve, line_cur, line_next)
    
    read_file.close()
    return dict_func_line, read_line_buf

def ProcFuncLine(line_context, line_num, list_line):
    func_ret, func_name = ExtractRetName(line_context)
    func_brief = ExtractBrief(line_context)
    func_params = ExtractParam(line_context)
    func_comment = GenerateComment(line_context, func_name, func_brief, func_ret, func_params)
    # delete ori comment
    if len(func_brief) != 0:
        del list_line[line_num - 1]
        line_num -= 1
    
    AddCommentToList(line_num, func_comment, list_line)


def ExtractRetName(line_context):
    # search type by name
    line_func = line_context[1]
    list_split = line_func.strip().split()
    if list_split.count('static') > 0:
        list_split.remove('static') #static func
    idx_name = 0
    for idx, str_value in enumerate(list_split):
        regexp_name = r'\b\('
        if re.search(regexp_name, str_value):
            idx_name = idx
            break
    str_name = list_split[idx_name].strip()
    
    str_name = str_name[0 : str_name.find('(')]
    
    str_ret = ''
    if idx_name >= 1:
        if idx_name >= 2 and "const" in list_split[idx_name -1]:
            str_ret += list_split[idx_name - 2]
        str_ret += list_split[idx_name - 1]
    return str_ret, str_name

def ExtractBrief(line_context):
    str_brief = line_context[0].strip()
    if '//' not in str_brief:
        return ''
    # need remove "//"
    idx_comm_flag = 0
    for i, ch in enumerate(str_brief):
        if ch != ' ' and ch != '/' and ch != '<':
            idx_comm_flag = i
            break
    str_brief = str_brief[idx_comm_flag : len(str_brief)]
    return str_brief

def ExtractParam(line_context):
    line_cur = line_context[1]
    reg_ret = re.findall(_regexp_bracket, line_cur)
    if len(reg_ret) <= 0:
        return
    reg_remove_bracket = reg_ret[0]
    reg_remove_bracket = reg_remove_bracket.replace('(', '')
    reg_remove_bracket = reg_remove_bracket.replace(')', '')
    line_split = reg_remove_bracket.split(",")

    for idx, value in enumerate(line_split):
        line_split[idx] = value.strip()
    return line_split


# I: non-ptr, non-ref, const
# O: ptr, ref
def GetIOType(strParamType):
    if "const " in strParamType:
        return '[I]'
    elif '*' in strParamType or '&' in strParamType:
        return '[O]'
    else:
        return '[I]'

def GenerateComment(line_context, str_name, str_brief, str_ret, list_param):
    left_space_len = len(line_context[1]) - len(line_context[1].lstrip())
    left_space = ""
    left_space = left_space.ljust(left_space_len)

    comment_func    = _list_comment_template[0] + str_name
    comment_brief   = _list_comment_template[1] + str_brief
    comment_param   = _list_comment_template[2]
    comment_ret     = _list_comment_template[3] + str_ret
    comment_end     = _list_comment_template[4]
    comment_param_empty = comment_param.replace("@param", "      ")
    list_param_info = []
    list_align_len = []
    list_io_type = []

    for idx_list, value_list in enumerate(list_param):
        value_list = value_list.strip()
        str_split = value_list.split()
        if 0 == len(str_split):
            continue
        param_name = str_split[-1]
        # get param name
        idx_name = 0
        for j, char_name in enumerate(param_name):
            ch_temp = ''
            ch_temp = char_name
            if ch_temp.isalpha():
                idx_name = j
                break
        str_non_alpha = param_name[0 : idx_name]
        param_name = param_name[idx_name : len(param_name)]

        # IO param align
        param_name_align = param_name
        if len(param_name_align) % 4 != 0:
            align_name_len = (len(param_name_align) + 4) & ~(4 - 1)
            list_align_len.append(align_name_len)
        else:
            list_align_len.append(len(param_name_align) + 4)
        param_type = value_list[0 : 0 - len(param_name) - 1] + str_non_alpha
        str_io_type = GetIOType(param_type)
        list_io_type.append(str_io_type)
        list_param_info.append(param_name_align)
    
    list_comment = []
    list_comment.append(left_space + comment_func + '\n')
    list_comment.append(left_space + comment_brief + '\n')
    max_align = 0
    if len(list_align_len) > 0:
        max_align = max(list_align_len)

    for i, str_value in enumerate(list_param_info):
        list_param_info[i] = str_value.ljust(max_align)
        list_param_info[i] += list_io_type[i]
        if i == 0:
            list_param_info[i] = comment_param + list_param_info[i]
        else:
            list_param_info[i] = comment_param_empty + list_param_info[i]
        list_comment.append(left_space + list_param_info[i] + '\n')
    list_comment.append(left_space + comment_ret + '\n')
    list_comment.append(left_space + comment_end + '\n')
    return list_comment


def AddCommentToList(line_num, func_comment, list_line):
    for line_comm in reversed(func_comment):
        list_line.insert(line_num, line_comm)


def GetCppFile(file_names):
    expanded = set()
    for file_name in file_names:
        if not os.path.isdir(file_name):
            expanded.add(file_name)
            continue
        
        for root, dirs, files in os.walk(file_name):
            for loop_file in files:
                full_name = os.path.join(root, loop_file)
                if full_name.startswith('.' + os.path.sep):
                    full_name = full_name[len('.' + os.path.sep): ]
                expanded.add(full_name)

    filtered_h = []
    filtered_cpp = []
    for file_name in expanded:
        if os.path.splitext(file_name)[1][1:] in _HeaderExtension:
            filtered_h.append(file_name)
        elif os.path.splitext(file_name)[1][1:] in _CppExtension:
            filtered_cpp.append(file_name)
    return filtered_h, filtered_cpp


def main():
    strPath = []
    if len(sys.argv) > 1:
        strPath.append(sys.argv[1])
    else:
        strPath.append("./test")
    file_h, file_cpp = GetCppFile(strPath)
    file_h.sort()
    file_cpp.sort()
    for idx, file_name in enumerate(file_h):
        ProcFile(file_name)
    
    for idx, file_name in enumerate(file_cpp):
        ProcFile(file_name)

if __name__ == '__main__':
    main()




    