from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import logout,login
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email 
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.conf import settings
from  task_app.models import TODO
from task_app.forms import TODOForm
from datetime import datetime
from .utils import get_plot
from django.db.models import Count
from django.db.models.functions import TruncDate
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging




@login_required(login_url='login')
def index(request):
    
    if request.user.is_authenticated:
        user = request.user    
        alltask =TODO.objects.filter(user=user).order_by('due_date')
        context={'tasks':alltask}
        return render(request, 'index.html',context)
    return render(request, 'index.html')


def add_task(request):
    if request.method == 'POST':
        form = TODOForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            desc = form.cleaned_data['description']
            
            # Parse the due_date string into a datetime object
            due_date_str = str(form.cleaned_data['due_date'])
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M:%S%z")

            status = form.cleaned_data.get('status', '')
            user = request.user

            todo_item = TODO(title=title, description=desc, due_date=due_date, user=user, status=status)
            todo_item.save()

            messages.success(request, "Task has been added successfully.")
            return redirect('index')
        else:
            # Display form errors individually
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

            # Return the form with errors
            return render(request, 'add_task.html', {'form': form})

    else:
        form = TODOForm()

    return render(request, 'add_task.html', {'form': form})


# for sign up OTP
logger = logging.getLogger(__name__)

@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        userotp = request.POST.get('otp')
        stored_otp = request.POST.get('stored_otp')  # Add this line
        if userotp == stored_otp:
            # Your verification logic goes here
            return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({'success': False}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
 
def Signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        

        # Validate username alphanumeric
        # Validate username alphanumeric and length
        if username is None or not username.isalnum() or len(username) > 10:
            messages.error(request, "Username should only contain numbers and letters and must be under 10 characters.")
            return redirect('signup')


        # Validate username length
        if len(username) > 10:
            messages.error(request, "Username must be under 10 characters.")
            return redirect('signup')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose a different one.')
            return redirect('signup')

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email address format')
            return redirect('signup')

        # Check if passwords match
        if pass1 != pass2:
            messages.error(request, 'Your passwords should be the same')
            return redirect('signup')

        # Additional email existence check (replace with your own logic)
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please choose a different one.')
            return redirect('signup')

        # Validate password strength using Django's built-in validators
        try:
            validate_password(pass1, user=None)
        except ValidationError as error:
            messages.error(request, ', '.join(error.messages))
            return redirect('signup')

       
        # Create and save the user
        
        # Create and save the user without OTP
        user = User.objects.create_user(username=username, email=email, password=pass1, first_name="", last_name="")

        # Generate and save the OTP in the user object
        otp = random.randint(100000, 999999)
        user.otp = otp
        user.save()

        # Log the OTP for debugging
        logger.info(f"User registered: {user.username}, Email: {user.email}, OTP: {otp}")

        # Send registration email
        subject = "Deliver info regarding registration"
        message = "You have been registered successfully and verified by otp"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message + f'\nYour OTP is: {otp}', from_email, recipient_list, fail_silently=False)

        messages.success(request, 'User has been registered.')
        return render(request, 'auth/verify.html', {'otp': otp, 'username': username, 'email': email, 'password1': pass1, 'password2': pass2})

    return render(request, 'auth/signup.html')

@csrf_exempt
def verify_login(request):
    if request.method == "POST":
        userotp = request.POST.get('otp')
        username= request.POST.get('username')
        password= request.POST.get('password')

        stored_otp = request.POST.get('stored_otp')  # Add this line
        user = authenticate(request,username= username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, 'You have been logged in successfully')
        if userotp == stored_otp:
            # Your verification logic goes here
            return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({'success': False}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def loginuser(request):
    if request.method== "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = User.objects.get(username=username).email

        
        
        if not username or not password:
            messages.error(request, 'Username and password are required')
            return render(request, 'auth/login.html')
       
        user = authenticate(request,username= username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                otp = random.randint(100000, 999999)
                user.otp = otp

                # Send registration email
                subject = "Deliver info regarding Login"
                message = "verified by otp"
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email]
                send_mail(subject, message + f'\nYour OTP is: {otp}', from_email, recipient_list, fail_silently=False)
                messages.success(request, 'You have been logged in successfully')
                return render(request, 'auth/verify_login.html', {'otp': otp, 'username': username, 'password': password})

            else:
                messages.error(request, 'Your account is disabled')
        
        else:
                messages.error(request, 'Invalid username or password')
         
                                           
    return  render (request, 'auth/login.html')

    
def logoutuser(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')    
    return redirect(reverse('login'))

                
class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/forget_password.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data['email']

        try:
            # Validate email format
            validate_email(email)

            # Check if the email exists in the database
            if User.objects.filter(email=email).exists():
                # Email exists, proceed with the original PasswordResetView behavior
                return super().form_valid(form)
            else:
                # Email doesn't exist in the database
                messages.error(self.request, 'The provided email does not exist in our records.')
        except ValidationError:
            # Invalid email format
            messages.error(self.request, 'Invalid email address format')

        return self.render_to_response(self.get_context_data(form=form))

    def render_to_response(self, context, **response_kwargs):
        return super().render_to_response(context, **response_kwargs)




def delete_todo(request,todo_id):
    todo= TODO.objects.get(id=todo_id)
    todo.delete()
    messages.success(request,'Task has been deleted')
    
    return redirect('index')

def change_todo(request,todo_id,status):
    todo= TODO.objects.get(id=todo_id)
    todo.status =status
    todo.save()
    
    
    return redirect('index')


def edit_todo(request, todo_id):
    todo = TODO.objects.get(id=todo_id)
    
    if request.method == 'POST':
        form = TODOForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully')
            return redirect('index')
    else:
        form = TODOForm(instance=todo)

    context = {'form': form, 'todo': todo}
    return render(request, 'edit_todo.html', context)

def chart(request):
    user = request.user
    qs = TODO.objects.filter(user=user)

    # Aggregate task count based on due_date
    task_counts = (
        qs.annotate(truncated_date=TruncDate("due_date"))
        .values("truncated_date")
        .annotate(count=Count("id"))
    )

    x = [entry["truncated_date"] for entry in task_counts]
    y = [entry["count"] for entry in task_counts]

    chart = get_plot(x, y)

    return render(request, 'chart.html', {'chart': chart})
