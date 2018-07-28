

from stark.service.stark import site,ModelStark

from app01.models import *


site.register(User)
site.register(Role)


class PermmissionConfig(ModelStark):

    list_display = ["title","url"]
    list_display_links = ["title"]
site.register(Permmission,PermmissionConfig)
