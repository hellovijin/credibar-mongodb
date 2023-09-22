from django.views.generic import CreateView
from django.shortcuts import render

class HomeView(CreateView):
    template_name = "credibar/home/index.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class EmailTemplateView(CreateView):
    template_name = "credibar/emails/signin-otp.html"
    def get(self, request, *args, **kwargs):
        self.template_name = "credibar/emails/{}.html".format( kwargs['slug'] )
        return render(request, self.template_name)