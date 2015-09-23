# mysqlwb2cb
Export ER model from MySQL Workbench to Chicago Boss ORM

Chicago Boss: http://chicagoboss.org

MySQL Workbench: https://www.mysql.com/products/workbench/

Installing:
* Get the file inflection.py from https://github.com/jpvanhal/inflection
* Install the file inflection.py as MySQL Workbench module
* Install the file boss_export.py as MySQL Workbench plugin
* Restart MySQL Workbench

Usage:
* Place a new text object
* Name it "cb application path"
* In the text field specify the path to your CB application
* Create ER model
* Export it with menu item Tools > Utilities

