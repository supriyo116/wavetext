from django.shortcuts import render,HttpResponse,get_object_or_404,redirect
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST,require_GET
from django.db.models import Q  # Import Q for complex queries
from django.views.decorators.csrf import csrf_exempt
import json


# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Group, GroupMessage

@login_required
def chatcenter(request):
    if request.method == 'POST':
        group_name = request.POST.get('name')
        members = request.POST.getlist('members')  # Get list of member IDs

        # Create the group
        group = Group(name=group_name)
        group.save()
        group.members.set(members)  # Add members to the group
        group.save()

        # Redirect back to the chat center after creating the group
        return redirect('/chatcenter/')

    # Handle GET requests
    search_query = request.GET.get('search', '')

    # Filter users based on the search query, excluding the current user
    if search_query:
        users = User.objects.exclude(username=request.user.username).filter(username__icontains=search_query)
        groups = Group.objects.filter(name__icontains=search_query)
    else:
        users = User.objects.exclude(username=request.user.username)
        groups = Group.objects.all()

    return render(request, 'index1.html', {'users': users, 'groups': groups})


@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('chatcenter')  # Redirect to the chat center page


@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            group.members.add(request.user)
            return redirect('chatcenter')


def update_contacts(request):
    # Fetch contacts for the logged-in user
    contacts = Contact.objects.filter(user=request.user).select_related('contact')

    # Prepare the data to be sent as JSON
    contact_data = []
    for contact in contacts:
        last_message = Message.objects.filter(
            sender=contact.contact,
            recipient=request.user
        ).order_by('-timestamp').first()
        contact_data.append({
            'username': contact.contact.username,
            'last_message': last_message.content if last_message else '',
            'last_message_timestamp': last_message.timestamp if last_message else '',
            'unread_count': Message.objects.filter(
                sender=contact.contact,
                recipient=request.user,
                read=False
            ).count()
        })

    return JsonResponse({'contacts': contact_data})



from .models import Message

@require_GET
@login_required
def chat_history(request, receiver_username):
    try:
        # Get the current user (sender) and the receiver
        sender = request.user
        receiver = User.objects.get(username=receiver_username)

        # Ensure the logged-in user is either the sender or the receiver
        if sender != request.user and receiver != request.user:
            return JsonResponse({'error': 'You are not authorized to view this chat.'}, status=403)

        # Fetch messages between the two users
        messages = Message.objects.filter(
            (Q(sender=sender) & Q(receiver=receiver)) |
            (Q(sender=receiver) & Q(receiver=sender))
        ).order_by('timestamp')

        # Create list of messages to return
        messages_list = [
            {
                'sender': msg.sender.username,  # Ensure it's a username
                'message': msg.message,  # Adjusted to your 'message' field
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            for msg in messages
        ]
        return JsonResponse({'messages': messages_list})

    except User.DoesNotExist:
        return JsonResponse({'error': 'Receiver does not exist.'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_users(request):
    users = User.objects.values('username')
    return JsonResponse({'users': list(users)})


import logging

logger = logging.getLogger(__name__)


from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Group
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def create_group(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        members = data.get('members', [])

        # Ensure the current user is in the list of members
        current_user_id = request.user.id
        if current_user_id not in members:
            return JsonResponse({'success': False, 'error': 'You must include yourself as a member of the group.'}, status=400)

        # Check for invalid characters
        invalid_characters = ' ,!@#$%^&*()_+={}[\\]|\\:;"\'<>,.?/~`'
        if any(char in invalid_characters for char in name):
            return JsonResponse({'success': False, 'error': 'Group name contains invalid characters.'})

        if not name:
            return JsonResponse({'success': False, 'error': 'Group name is required.'}, status=400)

        logger.debug(f"Creating group with name: {name}")
        logger.debug(f"Members: {members}")

        group = Group.objects.create(name=name)

        for member_id in members:
            user = User.objects.get(id=member_id)
            group.members.add(user)

        return JsonResponse({'success': True})

    except Exception as e:
        logger.error(f"Error creating group: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def group_chat_history(request, group_name):
    try:
        group = Group.objects.get(name=group_name)
        messages = GroupMessage.objects.filter(group=group).order_by('timestamp')
        message_list = [
            {
                'sender': msg.sender.username,
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]
        return JsonResponse({'messages': message_list})
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Group not found'}, status=404)



@login_required

def group_chat_view(request):
    # Get the current user
    user = request.user

    # Get the search query from the GET request
    search_query = request.GET.get('search', '')

    # Filter groups based on search query and membership
    if search_query:
        groups = Group.objects.filter(members=user, name__icontains=search_query)
    else:
        groups = Group.objects.filter(members=user)

    # Fetch all users for group creation
    users = User.objects.all()

    # Render the template with the filtered groups and users
    return render(request, 'gc.html', {
        'groups': groups,
        'users': users,
        'search_query': search_query,
    })

@login_required
def group_send_message(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        group_name = data.get('group_name')
        message_text = data.get('text')

        if not group_name or not message_text:
            return JsonResponse({'error': 'Group name and message text are required'}, status=400)

        group = Group.objects.filter(name=group_name).first()
        if not group:
            return JsonResponse({'error': 'Group not found'}, status=404)

        message = Message.objects.create(group=group, user=request.user, text=message_text)
        return JsonResponse({'success': True, 'message': {
            'sender': message.user.username,
            'message': message.text,
            'timestamp': message.timestamp.isoformat()
        }})

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def get_recent_messages(request):
    user = request.user  # Get the current user
    messages = Message.objects.filter(receiver=user).order_by('-timestamp')[:5]

    messages_data = [
        {
            'sender': msg.sender.username,
            'message': msg.message,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for msg in messages
    ]

    return JsonResponse({'messages': messages_data})