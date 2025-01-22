from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from django.contrib import messages
from django.shortcuts import redirect
from django.core.paginator import Paginator
from .models import Problem, Solution, UserProfile, Comment, Vote, Tag
from .forms import (
    ProblemForm, SolutionForm, UserProfileForm, UserForm,
    CommentForm, TagForm
)

def home(request):
    problems = Problem.objects.annotate(
        solution_count=Count('solutions')
    ).select_related('created_by').prefetch_related('tags')
    tag = request.GET.get('tag')
    difficulty = request.GET.get('difficulty')
    language = request.GET.get('language')
    
    if tag:
        problems = problems.filter(tags__slug=tag)
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    if language:
        problems = problems.filter(language__icontains=language)
    
    sort = request.GET.get('sort', '-created_at')
    if sort in ['views', '-views', 'solution_count', '-solution_count', 'created_at', '-created_at']:
        problems = problems.order_by(sort)
    
    paginator = Paginator(problems, 10)
    page = request.GET.get('page')
    problems = paginator.get_page(page)
    
    popular_tags = Tag.objects.annotate(
        problem_count=Count('problems')
    ).order_by('-problem_count')[:10]
    
    return render(request, 'core/home.html', {
        'problems': problems,
        'popular_tags': popular_tags,
        'current_tag': tag,
        'current_difficulty': difficulty,
        'current_language': language,
        'current_sort': sort,
    })

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Welcome to CodeConnect! Your account has been created successfully.')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def logout_view(request):
    if request.method in ('POST', 'GET'):
        logout(request)
        return redirect('home')

@login_required
def profile(request):
    user_problems = request.user.problem_set.annotate(
        solution_count=Count('solutions')
    ).order_by('-created_at')
    
    user_solutions = Solution.objects.filter(
        created_by=request.user
    ).select_related('problem').order_by('-created_at')
    
    bookmarked_problems = request.user.bookmarked_problems.all()
    
    profile = getattr(request.user, 'userprofile', None)
    
    return render(request, 'core/profile.html', {
        'profile': profile,
        'problems': user_problems,
        'solutions': user_solutions,
        'bookmarked_problems': bookmarked_problems,
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        
        # create an empty userProfile if not exists
        profile_instance = getattr(request.user, 'userprofile', None)
        if profile_instance is None:
            profile_instance = UserProfile(user=request.user)
        
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile_instance
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        # Handle the case where the user does not have a profile
        profile_instance = getattr(request.user, 'userprofile', None)
        if profile_instance is None:
            profile_instance = UserProfile(user=request.user)
        
        profile_form = UserProfileForm(instance=profile_instance)
    
    return render(request, 'core/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def problem_detail(request, pk, slug):
    problem = get_object_or_404(Problem, pk=pk, slug=slug)
    problem.views += 1
    problem.save()
    solutions = problem.solutions.select_related('created_by').prefetch_related('comment_set')
    comments = problem.comment_set.select_related('created_by').order_by('created_at')
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.problem = problem
            comment.created_by = request.user
            comment.save()
            messages.success(request, 'Your comment has been added.')
            return redirect('problem_detail', pk=pk, slug=slug)
    else:
        comment_form = CommentForm()
    
    return render(request, 'core/problem_detail.html', {
        'problem': problem,
        'solutions': solutions,
        'comments': comments,
        'comment_form': comment_form,
    })

@login_required
def create_problem(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.created_by = request.user
            problem.save()
            form.save_m2m() # save tags
            messages.success(request, 'Your problem has been posted successfully.')
            return redirect('problem_detail', pk=problem.pk, slug=problem.slug)
    else:
        form = ProblemForm()
    return render(request, 'core/create_problem.html', {'form': form})

@login_required
def add_solution(request, pk, slug):
    problem = get_object_or_404(Problem, pk=pk, slug=slug)
    if request.method == 'POST':
        form = SolutionForm(request.POST)
        if form.is_valid():
            solution = form.save(commit=False)
            solution.problem = problem
            solution.created_by = request.user
            solution.save()
            messages.success(request, 'Your solution has been posted successfully.')
            return redirect('problem_detail', pk=pk, slug=slug)
    else:
        form = SolutionForm()
    return render(request, 'core/add_solution.html', {
        'form': form,
        'problem': problem
    })

def solution_detail(request, pk):
    solution = get_object_or_404(Solution, pk=pk)
    return render(request, 'core/solution_detail.html', {
        'solution': solution
    })

@login_required
def vote_solution(request, solution_id):
    if request.method == 'POST':
        solution = get_object_or_404(Solution, id=solution_id)
        vote_type = request.POST.get('vote_type')
        
        if vote_type not in ['upvote', 'downvote']:
            return JsonResponse({'error': 'Invalid vote type'}, status=400)
        
        value = 1 if vote_type == 'upvote' else -1
        vote, created = Vote.objects.get_or_create(
            user=request.user,
            solution=solution,
            defaults={'value': value}
        )
        
        if not created:
            if vote.value == value:
                vote.delete()
                value = 0
            else:
                vote.value = value
                vote.save()
        
        solution.votes = Vote.objects.filter(solution=solution).aggregate(
            total=Sum('value')
        )['total'] or 0
        solution.save()
        
        return JsonResponse({
            'votes': solution.votes,
            'vote_type': 'none' if value == 0 else vote_type
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

'''@login_required
def bookmark_problem(request, pk):
    if request.method == 'POST':
        problem = get_object_or_404(Problem, pk=pk)
        if request.user in problem.bookmarked_by.all():
            problem.bookmarked_by.remove(request.user)
            bookmarked = False
        else:
            problem.bookmarked_by.add(request.user)
            bookmarked = True
        
        return JsonResponse({
            'bookmarked': bookmarked,
            'count': problem.bookmarked_by.count()
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
'''

'''@login_required
def accept_solution(request, solution_id):
    if request.method == 'POST':
        solution = get_object_or_404(Solution, id=solution_id)
        if request.user != solution.problem.created_by:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        # Remove accepted status from other solutions
        Solution.objects.filter(problem=solution.problem).update(is_accepted=False)
        solution.is_accepted = True
        solution.save()
        # Update problem status
        solution.problem.is_solved = True
        solution.problem.save()
        # Award reputation points
        solution.created_by.userprofile.reputation += 15
        solution.created_by.userprofile.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
'''
def search_problems(request):
    query = request.GET.get('q', '')
    if query:
        # Search for problems with a title, description, language, or tags containing the query
        problems = Problem.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(language__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct().values('title', 'language', 'slug')[:5]
        
        # If we find matching problems, return them as a JSON response
        if problems.exists():
            return JsonResponse({'success': True, 'data': list(problems)}, safe=False)
        
        # If no problems match, return a failure message
        return JsonResponse({'success': False, 'message': 'No results found for your query. Try being more specific.'})