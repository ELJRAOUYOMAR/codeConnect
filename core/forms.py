from django import forms
from django.contrib.auth.models import User
from .models import Problem, Solution, UserProfile, Comment, Tag

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'avatar', 'photo', 'github_url', 'linkedin_url', 'website', 'location')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class ProblemForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Problem
        fields = ('title', 'description', 'language', 'difficulty', 'tags')
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'markdown-editor',
                'rows': 10,
            }),
        }

class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ('content', 'code_snippet')
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'markdown-editor',
                'rows': 6,
                'required': True,  # Ensure the field is required
            }),
            'code_snippet': forms.Textarea(attrs={
                'class': 'code-editor',
                'rows': 10,
                # 'required': True,
                # 'id': 'id_content',
            }),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add a comment...'
            }),
        }

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }