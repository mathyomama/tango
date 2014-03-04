from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page

def with_underscore(attribute):
	return attribute.replace(' ', '_')

def without_underscore(attribute):
	return attribute.replace('_', ' ')

def index(request):
	context = RequestContext(request)

	category_likes_list = Category.objects.order_by('-likes')[:5]
	category_views_list = Category.objects.order_by('-views')[:5]
	context_dict = {'categories_likes':category_likes_list,
			'categories_views':category_views_list,
			}

	for category in category_likes_list:
		category.url = with_underscore(category.name)
	
	for category in category_views_list:
		category.url = with_underscore(category.name)

	return render_to_response('rango/index.html', context_dict, context)

def category(request, category_name_url):
	context = RequestContext(request)
	category_name = without_underscore(category_name_url)
	context_dict = {'category_name':category_name}

	try:
		category = Category.objects.get(name=category_name)
		pages = Page.objects.filter(category=category)
		context_dict['pages'] = pages
		context_dict['category'] = category
	except Category.DoesNotExist:
		pass

	return render_to_response('rango/category.html', context_dict, context)


def about(request):
	context = RequestContext(request)
	context_dict = {'quote': "You miss 100% of the shots you don't take.\n--Wayne Gretzky\n\t--Michael Scott"}
	return render_to_response('rango/about.html', context_dict, context)
