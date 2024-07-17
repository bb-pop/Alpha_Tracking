import base64
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from .forms import RegisterForm, CustomUserCreationForm, UserUpdateForm, PersonForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Person, CustomUser
import face_recognition
import numpy as np
import cv2
import os
import torch

# # Determine the absolute path to the model file
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# MODEL_PATH = os.path.join(BASE_DIR, 'facerecog', 'model', 'yolov5-face.pt')

# # Load YOLOv5 model
# model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH)

class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            number = form.cleaned_data['number']
            faceimage_data = request.POST.get('faceimage')
            format, imgstr = faceimage_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f"{name}.{ext}")

            # Generate face encoding
            face_encoding = self.generate_face_encoding(data)

            person = Person(name=name, number=number, faceimage=data, face_encode=face_encoding)
            person.save()
            return redirect('success')
        return render(request, 'register.html', {'form': form})

    def generate_face_encoding(self, image_file):
        image = face_recognition.load_image_file(image_file)
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            return face_encodings[0].tobytes()
        return None

class CaptureFaceView(View):
    def post(self, request):
        faceimage_data = request.POST.get('faceimage')
        return JsonResponse({'status': 'success', 'faceimage': faceimage_data})
    
class FaceDetectionView(View):
    def get(self, request):
        return render(request, 'face_detection.html')

    def post(self, request):
        faceimage_data = request.POST.get('faceimage')
        format, imgstr = faceimage_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        # Convert to OpenCV format
        nparr = np.frombuffer(data.read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Use face_recognition to detect faces
        face_locations = face_recognition.face_locations(img)

        if not face_locations:
            return JsonResponse({'status': 'fail', 'message': 'No face detected'})

        for (top, right, bottom, left) in face_locations:
            face_img = img[top:bottom, left:right]

            # Encode face using face_recognition
            face_encoding = self.generate_face_encoding(face_img)

            all_people = Person.objects.exclude(face_encode__isnull=True)
            known_face_encodings = [np.frombuffer(person.face_encode, dtype=np.float64) for person in all_people]
            known_names = [person.name for person in all_people]
            known_numbers = [person.number for person in all_people]
            known_faceimages = [person.faceimage.url for person in all_people]

            results = face_recognition.compare_faces(known_face_encodings, face_encoding)
            if True in results:
                match_index = results.index(True)
                matched_name = known_names[match_index]
                matched_number = known_numbers[match_index]
                matched_faceimage = known_faceimages[match_index]
                return JsonResponse({
                    'status': 'success',
                    'name': matched_name,
                    'number': matched_number,
                    'faceimage': matched_faceimage
                })

        return JsonResponse({'status': 'fail', 'message': 'Unknown face'})

    def generate_face_encoding(self, image):
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            return face_encodings[0].tobytes()
        return None

def success(request):
    return render(request, 'success.html')

def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register_user.html', {'form': form})

@login_required
def home(request):
    return render(request, 'home.html', {'user': request.user})

class CustomLoginView(auth_views.LoginView):
    template_name = 'login.html'

def is_manager(user):
    return user.role == 'manager'

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    managers = CustomUser.objects.filter(role='manager')
    cashiers = CustomUser.objects.filter(role='cashier')
    users = list(managers) + list(cashiers)
    return render(request, 'manager_dashboard.html', {'users': users})

@login_required
@user_passes_test(is_manager)
def user_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'user_detail.html', {'form': form, 'user': user})

# member list, edit, delete
def member_list(request):
    members = Person.objects.all()
    return render(request, 'member_list.html', {'members': members})

def member_edit(request, pk):
    member = get_object_or_404(Person, pk=pk)
    if request.method == "POST":
        form = PersonForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('member_list')
    else:
        form = PersonForm(instance=member)
    return render(request, 'member_edit.html', {'form': form, 'member': member})

def member_delete(request, pk):
    member = get_object_or_404(Person, pk=pk)
    if request.method == "POST":
        member.delete()
        return redirect('member_list')
    return render(request, 'member_confirm_delete.html', {'member': member})