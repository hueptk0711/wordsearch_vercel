from myapp.models import *
from myproject.word_generator.create_puzzle import createPuzzle
from django.http import HttpResponse, FileResponse
from django.contrib.auth.models import User, auth
from django.shortcuts import render, redirect # redirect: chuyen huong user toi page khac
from pdf2image import convert_from_path
from django.contrib import messages
import datetime
import io
import os
import sys

print(sys.executable)

# Create your views here.

# gửi request tới thư mục templates để tìm file index.html
def index(request):
    # dictionary
    return render(request, 'cover.html')

# sign up function
from django.contrib import messages

from django.contrib import messages

def register(request):  
    if request.method == 'POST':
        username = request.POST.get('username', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username already exists.')
            username_error = 'Username already exists.'
            return render(request, 'register.html', {'username_error': username_error})
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Email already exists.')
            email_error = 'Email already exists.'
            return render(request, 'register.html', {'email_error': email_error})
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            return redirect('login')
    else: 
        return render(request, 'register.html')
    
# log in function
def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        # Xác minh user
        user = auth.authenticate(username=username, password=password)

        # Kiểm tra xem người dùng có tồn tại không
        if user is not None:
            auth.login(request, user)
            return redirect('wordsearch')
        else:
            try:
                # Kiểm tra xem tên người dùng có tồn tại không
                User.objects.get(username=username)
                # Nếu tên người dùng tồn tại, nhưng mật khẩu không chính xác
                messages.error(request, 'Incorrect password.')
                login_password_error = 'Incorrect password.'
                return render(request, 'login.html', {'login_password_error': login_password_error})
            except User.DoesNotExist:
                # Nếu người dùng không tồn tại
                messages.error(request, 'Username does not exist.')
                login_username_error = 'Username does not exist.'
                return render(request, 'login.html', {'login_username_error': login_username_error})
    else:
        return render(request, 'login.html')

# log out
def logout(request):
    auth.logout(request) # log all user out of platform
    return redirect('/')

def wordsearch(request):
    return render(request, 'wordsearch.html')

# create function
def generate(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        lesson = request.POST['lesson']
        grade = request.POST['grade']
        # use get to present on standard dicts and is a way to fetch a value 
        # while providing a default if it does not exist
        create = request.POST.get('create-options')
        shape = request.POST.get('shape')
        str_level = request.POST.get('level-bar')
        puzzle = None
        print(create)
        # print(str_level)
        # print(shape)
        level = int(str_level)
        # Generate a unique filename based on the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # e.g., "20231101103045"
        pdf_filename = f"{timestamp}.pdf"

        # Path of the generated PDF
        user = request.user
        username = user.username
        user_folder = os.path.join('uploads/accounts', username)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder, exist_ok=True)
        path = os.path.join(user_folder, pdf_filename)  # Ensure this path matches your createPuzzle function

        # create puzzle
        if (create == 'answer'):    
            puzzle = createPuzzle(name, lesson, grade, shape, level)
            puzzle.save(path, solution=True)
        else:
            puzzle = createPuzzle(name, lesson, grade, shape, level)
            puzzle.save(path, solution=False)


        # convert first page of pdf to image to display on the website
        pages = convert_from_path(path, first_page=1, last_page=1)
        img_name = f"{timestamp}.png"
        account = 'accounts/' + username
        media_folder = os.path.join(settings.MEDIA_ROOT, account)
        if not os.path.exists(media_folder):
            os.makedirs(media_folder, exist_ok=True)
        # D:\VSC\word-search-AI\myproject\static\media\accounts
        img_path = os.path.join(media_folder, img_name)

        # save as image
        if pages:
            first_page = pages[0]
            first_page.save(img_path, 'PNG')

        # Save the generated PDF to the model PDFHistory
        pdf_history = PDFHistory(user=user, pdf=path, image = img_path)
        pdf_history.save()  
        return render(request, 'wordsearch.html', {
            'message': 'Puzzle created and saved successfully!',
            'image' : img_path, 'media_url':settings.MEDIA_URL,
            'pdf_filename': pdf_filename,
        })

    return render(request, 'wordsearch.html')

def guide(request):
    return render(request, 'guide.html')

def about_us(request):
    return render(request, 'about_us.html')

def home(request):
    return render(request, 'wordsearch.html')

# download function
def download(request, pdf_filename):
    # Construct the path to the PDF file in the media folder
    user = request.user
    username = user.username
    pdf_path = os.path.join('uploads/accounts', username, pdf_filename)
    
    # Ensure the file exists before trying to download
    if not os.path.exists(pdf_path):
        return HttpResponse("File not found", status=404)

    # Use FileResponse to send the file for download
    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=pdf_filename)
