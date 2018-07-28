from django.db import models

# Create your models here.


#  基于RBAC的WEB权限系统


class  User(models.Model):
    name=models.CharField(max_length=32)
    pwd=models.CharField(max_length=32)
    roles=models.ManyToManyField(to="Role")

    def __str__(self):
        return self.name


class Role(models.Model):

    title=models.CharField(max_length=32)
    permmissions=models.ManyToManyField(to="Permmission")

    def __str__(self):
        return self.title

class Permmission(models.Model):

    title=models.CharField(max_length=32)
    url=models.CharField(max_length=32)
    code=models.CharField(max_length=32,default="list")

    def __str__(self):
        return self.title

