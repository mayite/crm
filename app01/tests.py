from django.test import TestCase

# Create your tests here.


import re


# ret=re.search("/stark/app01/user/","/stark/app01/user/")
#
# print(ret)


re.search("^/user/$","/user/add/")