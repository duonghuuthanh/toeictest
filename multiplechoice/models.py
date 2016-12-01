from django.contrib.auth.models import User
from django.db import models

class Question(models.Model):
    content = models.CharField(max_length=500, 
                               help_text="The content of the question")
    help_text = models.CharField(max_length=200, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, help_text="This question is enable to users or not.")

class Answer(models.Model):
    content = models.CharField(max_length=200, 
                               help_text="The content of the answer")
    correct_percent = models.PositiveSmallIntegerField(default=0, 
                                                       help_text="100% -> correct answer")
    help_text = models.CharField(max_length=200, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question)

from django.core.exceptions import ValidationError
from datetime import datetime
from mptt.models import MPTTModel, TreeForeignKey

class MessageStatus:
    NOT_SENT, SENT = range(2)

    SENT_STATUS = ((NOT_SENT, 'Not Sent'),
                   (SENT, 'Sent'))

class Message(MPTTModel):
    from_user = models.ForeignKey(User, related_name="from_user_message")
    to_users = models.ManyToManyField(User, related_name="to_user_messages")
    subject = models.CharField(max_length=255)
    body = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    sent = models.PositiveSmallIntegerField(choices=MessageStatus.SENT_STATUS, default=MessageStatus.SENT)
    created_date = models.DateTimeField(auto_now_add=True)
    sent_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, db_index=True)

    def __str__(self):
        return "%s-from: %s-%s" % (str(self.pk), self.from_user.get_full_name(), self.subject)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

    @staticmethod
    def update_message(subject, 
                       body, 
                       from_user_id, 
                       to_user_ids=[], 
                       parent_id=None):
        if not isinstance(to_user_ids, list) or len(to_user_ids) == 0:
            raise ValidationError("To users are required.")

        # Add a message
        message = Message.objects.create(subject=subject, 
                                         body=body, 
                                         from_user_id=from_user_id, 
                                         parent_id=parent_id)

        # Update to user
        users = User.objects.filter(pk__in=to_user_ids)
        message.to_users.add(*users)

        return message

    @staticmethod
    def reply_message(message, 
                      from_user_id, 
                      reply_subject=None, 
                      reply_body=None, 
                      to_user_ids=None):
        if not message or \
           not message.to_users.filter(pk=from_user_id).exists() and \
           not from_user_id==message.from_user_id:
            raise ValidationError("Your cannot reply this email")

        reply = Message.objects.create(subject=reply_subject if reply_subject else message.subject,
                                       body=reply_body,
                                       from_user_id=from_user_id,
                                       parent=message)
     
        if to_user_ids:
            users = User.objects.filter(pk__in=to_user_ids).exclude(pk=from_user_id)
            reply.to_users.add(*users)
        else:
            users = message.to_users.exclude(pk=from_user_id)
        
            if from_user_id==message.from_user_id:
                reply.to_users.add(*users)
            else:
                reply.to_users.add(message.from_user, *users)

        return reply
            
    @staticmethod
    def get_sent_messages(user):
        messages = Message.objects.filter(active=True, 
                                          sent=True, 
                                          from_user=user, 
                                          parent__isnull=True,
                                          to_users__isnull=False)\
                                  .select_related('from_user')\
                                  .order_by('-created_date')

        return messages

    @staticmethod
    def get_received_messages(user):
        messages = Message.objects.filter(active=True, 
                                          sent=True, 
                                          to_users=user, 
                                          parent__isnull=True)\
                                  .select_related('from_user')\
                                  .order_by('-created_date')

        return messages

    @staticmethod
    def get_reply_messages(message, from_user=None):
        messages = message.get_children()\
                          .filter(active=True, 
                                  sent=True)\
                          .select_related('from_user')\
                          .order_by('created_date')

        if from_user:
            messages = messages.filter(from_user=from_user)

        return messages

    @staticmethod
    def serializer(message):
        to_users = []
        for user in message.to_users.all():
            to_users.append({
                "id": user.pk,
                "first_name": user.first_name,
                "last_name": user.last_name
            })

        return  {
            "subject": message.subject,
            "body": message.body,
            "sent_date": message.created_date,
            "from_user": {
                "id": message.from_user.pk,
                "first_name": message.from_user.first_name,
                "last_name": message.from_user.last_name
            },
            "to_users": to_users
        }

class UserMessageStatus(models.Model):
    user = models.ForeignKey(User)
    message = models.ForeignKey(Message)
    read = models.BooleanField(default=True)
    read_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'message')

    def __str__(self):
        return "%s-%s-%s" % (self.user.get_full_name(), self.message.title, self.read)

    @staticmethod
    def update_user_message_status(user, message, read=None, deleted=None):
        u_msg, _ = UserMessageStatus.objects.get_or_create(user=user, message=message)

        if read is not None:
            u_msg.read = read
            u_msg.read_date = datetime.now()
        if deleted:
            u_msg = deleted
            u_msg.deleted_date = datetime.now()

        u_msg.save()

    @staticmethod
    def get_user_message_status(user, message):
        u_msg = UserMessageStatus.objects.get(user=user, message=message)
        
        return {
            "read": u_msg.read,
            "deleted": u_msg.deleted
        }