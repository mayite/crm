
from django.conf.urls import url

from django.shortcuts import HttpResponse,redirect,render

from django.utils.safestring import mark_safe
from django.urls import reverse

from stark.utils.page import Pagination
from django.db.models import Q

class Showlist(object):
    def __init__(self,conf_obj,queryset,request):
        self.conf_obj=conf_obj
        self.queryset=queryset
        self.request=request

        # 分页
        current_page=self.request.GET.get("page")
        pagination=Pagination(current_page,self.queryset.count(),self.request.GET,per_page_num=10)
        self.pagination=pagination

        self.page_queryset=self.queryset[self.pagination.start:self.pagination.end]

    def get_header(self):
        # 处理表头

        # header_list=["名称","价格","出版社"]
        header_list = []

        for field_or_func in self.conf_obj.get_new_list_display():  # ["title","price","publish",delete_col]

            if isinstance(field_or_func, str):

                if field_or_func == "__str__":
                    val = self.conf_obj.model._meta.model_name.upper()
                else:

                    field_obj = self.conf_obj.model._meta.get_field(field_or_func)
                    val = field_obj.verbose_name
            else:
                val = field_or_func(self.conf_obj, is_header=True)

            header_list.append(val)
        return header_list
    def get_body(self):
        #  处理表单数据
        data_list = []
        for obj in self.page_queryset:  # [obj1,obj2,obj3]
            temp = []

            for field_or_func in self.conf_obj.get_new_list_display():  # list_display = ["title","price","publish",delete_col]

                if isinstance(field_or_func, str):
                    val = getattr(obj, field_or_func)
                    if field_or_func in self.conf_obj.list_display_links:
                        val = mark_safe("<a href='%s'>%s</a>" % (self.conf_obj.get_reverse_url("change", obj), val))
                else:
                    val = field_or_func(self.conf_obj, obj)

                temp.append(val)
            data_list.append(temp)

        print(data_list)
        return data_list
    def get_actions(self):
        temp=[]
        for func in self.conf_obj.actions:# [patch_delete,]
            temp.append({
                "name":func.__name__,
                "desc":func.desc
            })

        return temp  #  [{"name":"patch_delete","desc":"批量删除"},]
    def get_filter_links(self):

        print("self.conf_obj.list_filter",self.conf_obj.list_filter) #  ['publish', 'authors']

        links_dict={}



        for filter_field in self.conf_obj.list_filter: # ['publish', 'authors']
            filter_field_obj=self.conf_obj.model._meta.get_field(filter_field)
            print(filter_field_obj)
            print(type(filter_field_obj))

            from django.db.models.fields.related import ForeignKey
            print("rel",filter_field_obj.rel.to)
            queryset=filter_field_obj.rel.to.objects.all()
            print("queryset",queryset)
            temp=[]

            import copy

            params=copy.deepcopy(self.request.GET)

            # 渲染标签

            current_filter_field_id=self.request.GET.get(filter_field)

            #  all 的链接标签
            params2 = copy.deepcopy(self.request.GET)
            if filter_field in params2:
                params2.pop(filter_field)
                all_link="<a href='?%s'>All</a>"%params2.urlencode()
            else:
                all_link = "<a href=''>All</a>"
            temp.append(all_link)

            for obj in queryset:
                params[filter_field]=obj.pk
                _url=params.urlencode()

                if current_filter_field_id==str(obj.pk):
                    s = "<a class='item active' href='?%s'>%s</a>" % (_url, str(obj))
                else:
                    s="<a class='item' href='?%s'>%s</a>"%(_url,str(obj))
                temp.append(s)

            links_dict[filter_field]=temp


        return  links_dict

class ModelStark(): # 默认配置类对象


    def __init__(self,model):
        self.model=model
        self.model_name = self.model._meta.model_name
        self.app_label = self.model._meta.app_label
        self.app_model_name=(self.app_label,self.model_name)
        self.key_word=""
    list_display=["__str__"]
    list_display_links=[]
    model_form_class=[]
    actions=[]

    search_fields=[]
    list_filter=[]


    # 反向解析出增删改查的url


    # # 删除url
    # def get_delete_url(self,obj):
    #     url_name = "%s_%s_delete" % self.app_model_name
    #     _url = reverse(url_name, args=(obj.pk,))
    #
    #     return _url
    #
    # # 编辑url
    # def get_change_url(self, obj):
    #     url_name = "%s_%s_change" % self.app_model_name
    #     _url = reverse(url_name, args=(obj.pk,))
    #
    #     return _url
    #
    #
    # # 查看url
    # def get_list_url(self):
    #     url_name = "%s_%s_list" % self.app_model_name
    #     _url = reverse(url_name)
    #
    #     return _url
    #
    # # 添加url
    # def get_add_url(self, obj):
    #     url_name = "%s_%s_add" % self.app_model_name
    #     _url = reverse(url_name, args=(obj.pk,))
    #
    #     return _url


    def get_reverse_url(self, type,obj=None):

        url_name = "%s_%s_%s" % (self.app_label,self.model_name,type)
        if obj:
            _url = reverse(url_name, args=(obj.pk,))
        else:
            _url = reverse(url_name)

        return _url

    #  选择，删除，编辑按钮
    def delete_col(self,obj=None,is_header=False):

        if is_header:
            return "删除"

        return mark_safe("<a href='%s'>删除</a>"%self.get_reverse_url("delete",obj))

    def edit_col(self,obj=None,is_header=False):
        if is_header:
            return "编辑"

        return mark_safe("<a href='%s'>编辑</a>"%(self.get_reverse_url("change",obj)))

    def check_col(self,obj=None,is_header=False):
        if is_header:
            return "选择"

        return mark_safe("<input type='checkbox' name='selected_action' value='%s'>"%obj.pk)


    def get_new_list_display(self):
        new_list_display=[]

        new_list_display.extend(self.list_display)
        if not self.list_display_links:
            new_list_display.append(ModelStark.edit_col)
        new_list_display.append(ModelStark.delete_col)
        new_list_display.insert(0,ModelStark.check_col)

        return new_list_display


    def search_filter(self,request,queryset):
        # search 操作

        key_word = request.GET.get("q")

        print(self.search_fields)  # ["title","price"]
        self.key_word = ""
        if key_word:

            self.key_word=key_word

            search_condition = Q()
            search_condition.connector = "or"
            for field in self.search_fields:
                search_condition.children.append((field + "__icontains", key_word))

            queryset = queryset.filter(search_condition)

        return queryset

    def filter_list(self,request,queryset):
        # filter  操作
        filter_condition = Q()
        for key, val in request.GET.items():  # publish=2&authors=1

            if key in ["page","q"]:
                continue

            filter_condition.children.append((key, val))

        if filter_condition:
            try:
                queryset=queryset.filter(filter_condition)
            except Exception:
                pass


        return queryset

    def list_view(self,request):


        #  action操作
        if request.method=="POST":
            action=request.POST.get("action")
            pk_list=request.POST.getlist("selected_action")
            queryset=self.model.objects.filter(pk__in=pk_list)

            func=getattr(self,action)

            func(request,queryset)

        # 用户访问的模型表：  self.model
        print("self.model:", self.model)
        queryset = self.model.objects.all()
        print("self.list_display", self.list_display)  # ["nid","title","price","publish"]

        # search 操作
        queryset=self.search_filter(request,queryset)

        queryset=self.filter_list(request,queryset)


        showlist=Showlist(self,queryset,request)

        #   获取添加url
        add_url=self.get_reverse_url("add")

        return render(request, "stark/list_view.html", locals())

    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class
        else:
            from django import forms

            class ModelFormDemo(forms.ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"

            return ModelFormDemo


    def add_view(self, request):
        """
        if GET请求：
           GET请求：
           form = BookModelForm()
           form:渲染

        if POST请求:
               form = BookModelForm(request.POST)
               form.is_valid()
               form.save()  # 添加数据 create

        :param request:
        :return:
        """
        ModelFormDemo=self.get_model_form_class()

        from  django.forms.boundfield import BoundField
        from  django.forms.models import ModelChoiceField
        if request.method=="GET":
            form=ModelFormDemo()


            for bfield in form :

                # print(type(bfield.field))

                if isinstance(bfield.field,ModelChoiceField):
                    bfield.is_pop=True

                    filed_rel_model=self.model._meta.get_field(bfield.name).rel.to
                    model_name=filed_rel_model._meta.model_name
                    app_label=filed_rel_model._meta.app_label

                    _url=reverse("%s_%s_add"%(app_label,model_name))
                    bfield.url=_url+"?pop_back_id="+bfield.auto_id


            return render(request,"stark/add_view.html",locals())
        else:
            form=ModelFormDemo(request.POST)
            if form.is_valid():
                obj=form.save()
                pop_back_id=request.GET.get("pop_back_id")
                if pop_back_id:
                    pk=obj.pk
                    text=str(obj)
                    return render(request,"stark/pop.html",locals())

                return redirect(self.get_reverse_url("list"))
            else:
                return render(request, "stark/add_view.html", locals())


    def change_view(self, request,id):
       """
        edit_book = Book.objects.get(pk=id)
        GET：
            form = BookModelForm(instance=edit_book)
            form:渲染

        POST:
            form = BookModelForm(request.POST, instance=edit_book)
            form.is_valid
            form.save()  # 更新数据 update
       :param request:
       :param id:
       :return:
       """

       ModelFormDemo=self.get_model_form_class()
       edit_obj=self.model.objects.get(pk=id)
       if request.method=="GET":

           form=ModelFormDemo(instance=edit_obj)
           return render(request, "stark/change_view.html",locals())
       else:
           form=ModelFormDemo(data=request.POST,instance=edit_obj)
           if form.is_valid():
               form.save()
               return redirect(self.get_reverse_url("list"))
           else:
               return render(request, "stark/change_view.html", locals())



    def delete_view(self, request,id):

        if request.method=="POST":
            self.model.objects.get(pk=id).delete()
            return redirect(self.get_reverse_url("list"))

        list_url=self.get_reverse_url("list")
        return render(request,"stark/delete_view.html",locals())


    def get_urls(self):


        temp=[
            url("^$",self.list_view,name="%s_%s_list"%(self.app_model_name)),
            url("^add/$",self.add_view,name="%s_%s_add"%(self.app_model_name)),
            url("^(\d+)/change/$",self.change_view,name="%s_%s_change"%(self.app_model_name)),
            url("^(\d+)/delete/$",self.delete_view,name="%s_%s_delete"%(self.app_model_name)),

        ]
        '''




        '''

        return temp


    @property
    def urls(self):


        return self.get_urls(),None,None




class StarkSite(object):

    def __init__(self, name='admin'):
          self._registry = {}

    def register(self, model, admin_class=None, **options):
        if not admin_class:
            admin_class = ModelStark   # 配置类

        self._registry[model] = admin_class(model)

    # {Book:BookConfig(Book),Publish:ModelAdmin(Publish)}



    def get_urls(self):

        temp = [

        ]


        for model_class, config_obj in self._registry.items():
            print("===>", model_class, config_obj)

            model_name = model_class._meta.model_name
            app_label = model_class._meta.app_label
            print("===>", app_label, model_name)

            temp.append(url(r'^%s/%s/' % (app_label, model_name),config_obj.urls))

        '''
        创建url：

            url("app01/book/$",self.list_view,name="app01_book_list"),
            url("app01/book/add$",self.add_view,name="app01_book_add"),
            url("app01/book/(\d+)/change/$",self.change_view),
            url("app01/book/(\d+)/delete/$",self.delete_view),



            url("app01/publish/$",self.list_view,name="app01_publish_list"),
            url("app01/publish/add$",self.add_view,name="app01_publish_add"),
            url("app01/publish/(\d+)/change/$",self.change_view),
            url("app01/publish/(\d+)/delete/$",self.delete_view),



        '''

        return temp

    @property
    def urls(self):

        return self.get_urls(),None,None

site=StarkSite()