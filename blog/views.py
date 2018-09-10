from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import (TemplateView, ListView, DetailView,
                                  CreateView, UpdateView, DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class AboutView(TemplateView):
    template_name = 'about.html'


class PostListView(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
        # translates into the following SQL: ELECT * FROM blog WHERE published_date
        # Grap the Post model, all the objects there, filter them with upper condition
        # __lte => less than or equal to (doc: Field lookups)
        # '-published_date' ==> - 부호 --> descending order

class PostDetailView(DetailView):
    model = Post


# Create나 Update는 Login을 요구함
class CreatePostView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    # success_url : Delete 후에 어디로 갈지
    success_url = reverse_lazy('post_list')


class DraftListView(LoginRequiredMixin, ListView):
    template_name = 'post_draft_list.html'
    login_url = '/login/'
    redirect_field_name = 'blog/post_list.html'
    model = Post

    # Post들 중에
    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')

#################################################
#################################################
@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            # models.py 의 Comment class에 post=models.ForeignKey
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/comment_form.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    # comment.delete하면 comment.post.pk 가 없어지므로 post_pk에 미리 저장
    comment.delete()
    return redirect('post_detail', pk=post_pk)
