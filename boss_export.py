# MySQL Workbench Plugin
# boss_export.py
# Written in MySQL Workbench 6.3.4
#
# Copyright (c) 2015 Konstantin Gorshkov
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from inflection_grt import *
from wb import *
import grt

ModuleInfo = DefineModule('boss_export', description="Boss export", author="Konstantin Gorshkov", version="0.1")

@ModuleInfo.plugin("boss_export", "Export to Chicago Boss App", input=[wbinputs.currentModel()], pluginMenu="Utilities")
@ModuleInfo.export(grt.INT, grt.classes.workbench_physical_Model)
def boss_export(model):
    path = get_filename(model)
    if path != "":
        write_files(path, (prepare_files(prepare_relationships(model))))
    return 0

def prepare_relationships(pm):
    belongs_to = {}
    has = {}
    tables = []
    has_through = {}
    for tab in pm.catalog.schemata[0].tables:
        belongs_to[tab] = []
        has[tab] = []
        has_through[tab] = []
    for tab in pm.catalog.schemata[0].tables:
        tables.append(tab)
        if hasattr(tab, 'foreignKeys'):
            is_has_through = len(tab.foreignKeys) == 2 and not has_id_col(tab.columns)
            for key in tab.foreignKeys:
                belongs_to[tab].append(key)
                for ref in key.referencedColumns:
                    has[ref.owner].append(key)
                    if is_has_through:
                        has_through[ref.owner].append(tab)
                
    return {'belongs_to': belongs_to, 'has': has, 'tables': tables, 'has_through': has_through}

def prepare_files(preparedModel):
    belongs_to = preparedModel['belongs_to']
    has = preparedModel['has']
    tables = preparedModel['tables']
    has_through = preparedModel['has_through']
    outputs = []
    #prepare files to export
    for tab in tables:
        moduleName = singularize(tab.name)
        columns = tab.columns
        columnVars = ["Id"]
        for column in columns:
            if column.name != 'id':
                columnVars.append(show_module_param(column, belongs_to[tab]))
        vars = (', '.join([str(i) for i in columnVars]))
        output = "-module(%s, [%s]).\n-compile(export_all).\n" % (moduleName, vars)
        for key in belongs_to[tab]:
            output += "-belongs_to(%s).\n" % (key.referencedColumns[0].owner.name)
        for key in has[tab]:
            if key.many == 0:
                output += "-has({%s, 1}).\n" % (key.owner.name)
            else:
                output += "-has({%s, many}).\n" % (pluralize(key.owner.name))
        for key in has_through[tab]:
            output += show_through_fun(tab, key)
        outputs.append({'filename': "src/model/" + moduleName + ".erl", 'contents': output})
    return outputs

def has_id_col(columns):
    for col in columns:
        if col.name == 'id':
            return True
    return False

def show_through_fun(tab, through_tab):
    fks = through_tab.foreignKeys
    cols = tab.columns
    for fk in fks:
        tab_ = fk.referencedColumns[0].owner
        if tab_ != tab:
            through_col = fk.columns[0].name
            target_tab = tab_
    output =  "\n{}() ->\n".format(pluralize(target_tab.name))
    output += "\tIds = [X:{}() || X <- {}()],\n".format(through_col, pluralize(through_tab.name))
    output += "\tboss_db:find({}, [{{id, 'in', Ids}}]).\n".format(target_tab.name)
    return output

def show_module_param(col, fkeys):
    var = camelize(col.name)
    for key in fkeys:
        if col in key.columns:
            return var
    return var + show_module_param_type(col)

def show_module_param_type(col):
    if any_type(col, ["VARCHAR"]):
        return "::string()"
    elif is_type(col, "TIMESTAMP"):
        return "::timestamp()"
    elif is_type(col, "DATETIME"):
        return "::datetime()"
    elif any_type(col, ["INT"]):
        return "::integer()"
    elif is_type(col, "DATE"):
        return "::date()"
    elif is_type(col, "BINARY"):
        return "::binary()"
    elif is_type(col, "FLOAT"):
        return "::float()"
    elif is_type(col, "BOOL"):
        return "::boolean()"
    else:
        return ""

def is_type(col, type):
    return col.formattedRawType.find(type) >= 0

def any_type(col, types):
    for type in types:
        if is_type(col, type):
            return True
    return False

def write_files(path, pmodel):
    for filedata in pmodel:
        filename = path + "/" + filedata['filename']
        print "Write file: %s" % (filename)
        with open(filename, 'w') as file:
            file.write(filedata['contents'])

def get_filename(model):
    for diagram in model.diagrams:
        for figure in diagram.figures:
            if figure.name == 'cb application path':
                return figure.text
    return ""


