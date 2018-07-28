from django.shortcuts import render,redirect

# Create your views here.

from app01.models import User



def login(request):

   if request.method=="POST":
        user=request.POST.get("user")
        pwd=request.POST.get("pwd")

        user=User.objects.filter(name=user,pwd=pwd).first()
        if user:

            # 保存登陆状态
            request.session["user_id"]=user.pk
            request.session["username"]=user.name

            # 获取当前登陆用户的所有权限列表

            permission_list=[]
            permissions=user.roles.all().values("permmissions__url","permmissions__code","permmissions__title").distinct()
            # print(permissions)
            permisssion_menu_list=[]
            for item in permissions:
                permission_list.append(item.get("permmissions__url"))


                if item.get("permmissions__code")=="list":
                    permisssion_menu_list.append({
                        "url":item.get("permmissions__url"),
                        "title":item.get("permmissions__title"),
                    })

            print(permission_list)

            print(permisssion_menu_list)

            # 注册权限列表到session中
            request.session["permission_list"]=permission_list

            # 注册权限字典到字典中

            request.session["permisssion_menu_list"]=permisssion_menu_list



            return redirect("/index/")


   return render(request,"login.html")



def index(request):


    return render(request,"index.html")



def logout(request):

    request.session.flush()

    return redirect("/index/")