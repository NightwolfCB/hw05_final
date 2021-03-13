from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube import settings

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:11]
    paginator = Paginator(posts, settings.PAGE_SIZE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group,
        'posts': posts,
        'page': page,
        'paginator': paginator
    })


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_latest = author.posts.all()
    post_count = author.posts.count()
    paginator = Paginator(posts_latest, settings.PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if (request.user.id is not None
            and Follow.objects.filter(
                author__following__user=request.user).exists()):
        following = True
    else:
        following = False
    context = {
        'page': page,
        'paginator': paginator,
        'post_count': post_count,
        'author': author,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'author': post.author,
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if post.author.id != request.user.id:
        return redirect('posts:post', username, post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post', username, post_id)
    return render(request, 'posts/post_edit.html',
                  {'post': post, 'form': form}
                  )


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post', username, post_id)


@login_required
def follow_index(request):
    user = get_object_or_404(User, username=request.user.username)
    post_list = Post.objects.filter(author__following__user=user)
    paginator = Paginator(post_list, settings.PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/follow.html',
        {'page': page,
         'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(author=user, user=request.user)
    if follow.exists() or request.user == user:
        return redirect('posts:profile', username=username)
    else:
        Follow.objects.create(
            author=user,
            user=request.user
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(author=user, user=request.user)
    if follow.exists() or request.user != user:
        follow.delete()
    return redirect('posts:profile', username=username)
