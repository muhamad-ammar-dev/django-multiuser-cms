from urllib import request

from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from taggit.models import Tag
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from accounts.models import Profile

# Create your views here.
@login_required
def home(request):
    search = request.GET.get('search')
    if search:
        all_blogs = Blog.objects.filter(Q(title__icontains=search) & Q(content__icontains=search)).order_by('-id')
    else:
        all_blogs = Blog.objects.all().order_by('-id')
    page = request.GET.get('page', 1)
    pag = Paginator(all_blogs, 2)  
    try:
        posts = pag.page(page)
    except PageNotAnInteger:
        posts = pag.page(1)
    except EmptyPage:
        posts = pag.page(pag.num_pages)
    return render(request, 'index.html', {'all_blogs': posts})

def detail_blog(request, pk):
    blog = Blog.objects.get(id=pk)
    comments = Comment.objects.filter(blog=blog, active=True)
    return render(request, 'detail.html', {'blog': blog, 'comments': comments})

def get_tags(request, tag_slug):
    all_blogs = Blog.objects.all().order_by('-id')

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        blogs = all_blogs.filter(tags__in=[tag])
    
    context = {
        'all_blogs': blogs,
        'tag': tag,
    }

    return render(request, 'tags.html', context)

def save_comment(request):
    if request.POST:
        pk = request.POST.get('id')
        message = request.POST.get('message')
        blog = Blog.objects.get(id=pk)
        user = request.user
        new_comment = Comment.objects.create(comment=message, active=True, blog=blog, user=user)
        new_comment.save()
        return redirect('detail_blog', pk)
    
def delete_comment(request):
    if request.POST:
        pk = request.POST.get('id-delete')
        id_blog = request.POST.get('id')
        comment = Comment.objects.get(id=pk)
        comment.delete()
        return redirect('detail_blog', id_blog)

def edit_blog(request, pk):
    blog = Blog.objects.get(id=pk)
    if request.POST:
        form = EditBlog(request.POST, request.FILES, instance=blog)
        if form.errors:
            messages.warning(request, f'{form.errors}')
        if form.is_valid():
            form.save()
            messages.success(request, 'Your blog has been updated successfully!')
            return redirect('detail_blog', blog.id)
    else:
        form = EditBlog(instance=blog)
    return render(request, 'edit_post.html', {'form': form, 'blog': blog})  

def delete_blog(request, pk):
    blog = Blog.objects.get(id=pk).delete()
    messages.success(request, 'Your post has been deleted successfully!')
    return redirect('home')

@login_required
def create_post(request):
    if request.POST:
        form = CreatePost(request.POST, request.FILES)
        if form.errors:
            messages.warning(request, f'{form.errors}')
        if form.is_valid():
            new = form.save(commit=False)
            new.author = request.user
            new.save()
            messages.success(request, 'Your blog has been created successfully!')
            return redirect('home')
    else:
        form = CreatePost()
    return render(request, 'create_post.html', {'form': form})  

@login_required
def about(request):
    profile = Profile.objects.all()
    about_page = About.objects.all().first()
    return render(request, 'about.html', {'about': about_page, 'profile': profile})
    
@login_required
def contact(request):
    contact_info = ContactInfo.objects.all().first()
    if request.POST:
        form = ContactUsForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.user = request.user
            new.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('home')
    else:
        form = ContactUsForm()
    return render(request, 'contact.html', {'contact': contact_info, 'form': form})
    