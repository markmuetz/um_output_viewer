# Not working
#../post_proc1.pbs.o3870117
#--------------------------------------------------------------------------------
#Traceback (most recent call last):
#  File "converter.py", line 5, in <module>
#    from config import config
#  File "/fs2/n02/n02/mmuetz/scripts/um_output_viewer/config.py", line 3, in <module>
#    from collections import OrderedDict
#  File "/home/y07/y07/cse/anaconda/2.2.0-python2/lib/python2.7/collections.py", line 9, in <module>
#    from operator import itemgetter as _itemgetter, eq as _eq
#ImportError: /fs2/n02/n02/mmuetz/scripts/um_output_viewer/umov.venv/lib/python2.7/lib-dynload/operator.so: undefined symbol: _PyUnicodeUCS4_AsDefaultEncodedString
#--------------------------------------------------------------------------------
#
#module load python-compute
#source umov.venv/bin/activate

# Not recommended:
# http://www.archer.ac.uk/documentation/user-guide/python.php#native
# But it works.
module load anaconda-compute

python converter.py
