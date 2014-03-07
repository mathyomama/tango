from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from django.core.urlresolvers import reverse

def with_underscore(attribute):
	return attribute.replace(' ', '_')

def without_underscore(attribute):
	return attribute.replace('_', ' ')

def add_category(request):
	context = RequestContext(request)

	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return HttpResponseRedirect(reverse("index"))
		else:
			print form.errors
	else:
		form = CategoryForm()
	
	return render_to_response('rango/add_category.html', {'form':form}, context)

def add_page(request, category_name_url):
	context = RequestContext(request)

	category_name = without_underscore(category_name_url)
	if request.method == 'POST':
		form = PageForm(request.POST)

		if form.is_valid():
			# Not all fields are automatically populated! So no commit right away, whatever that means, I guess we have to check a few fields first
			page = form.save(commit=False)
			try:
				cat = Category.objects.get(name=category_name)
				page.category = cat
			except Category.DoesNotExist:
				return render_to_response('rango/add_category.html', {}, context)

			page.views = 0
			page.save()
			return HttpResponseRedirect(reverse('category', args=[category_name_url]))
			#return category(request, category_name_url)
		else:
			print form.errors
			return index(request)
	else:
		form = PageForm()
	
	return render_to_response('rango/add_page.html', {'category_name_url':category_name_url, 'category_name':category_name, 'form':form}, context)

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
