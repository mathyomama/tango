from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

def with_underscore(attribute):
	return attribute.replace(' ', '_')

def without_underscore(attribute):
	return attribute.replace('_', ' ')

@login_required
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

@login_required
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
	page_views_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories_likes':category_likes_list,
			'pages_views':page_views_list,
			}

	for category in category_likes_list:
		category.url = with_underscore(category.name)

	return render_to_response('rango/index.html', context_dict, context)

def category(request, category_name_url):
	context = RequestContext(request)
	category_name = without_underscore(category_name_url)
	context_dict = {'category_name':category_name, 'category_name_url':category_name_url}

	try:
		category = Category.objects.get(name=category_name)
		pages = Page.objects.filter(category=category)
		context_dict['pages'] = pages
		context_dict['category'] = category
	except Category.DoesNotExist:
		pass

	return render_to_response('rango/category.html', context_dict, context)

def view_categories(request):
	context = RequestContext(request)
	all_categories = Category.objects.order_by('-views')[:]
	context_dict = {'all_categories':all_categories}
	for category in all_categories:
		category.url = with_underscore(category.name)
	
	return render_to_response('rango/categories.html', context_dict, context)

def about(request):
	context = RequestContext(request)
	context_dict = {'quote': "You miss 100% of the shots you don't take.\n--Wayne Gretzky\n\t--Michael Scott"}
	return render_to_response('rango/about.html', context_dict, context)

def register(request):
	context = RequestContext(request)
	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()
			registered = True

		else:
			print user_form.errors, profile_form.errors
	
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
	
	return render_to_response(
			'rango/register.html',
			{'user_form':user_form, 'profile_form':profile_form, 'registered':registered},
			context)

def user_login(request):
	context = RequestContext(request)

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('index'))
			else:
				return HttpResponse("Your Rango account is disabled.")
		else:
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied.")
	else:
			return render_to_response('rango/login.html', {}, context)

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/rango/')
