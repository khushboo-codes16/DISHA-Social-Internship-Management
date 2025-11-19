"""
Notification Manager
Handles real-time notifications and updates
"""

from datetime import datetime


class NotificationManager:
    """Manage notifications and real-time updates"""
    
    def __init__(self, db):
        self.db = db
    
    def create_notification(self, user_id, notification_type, title, message, data=None):
        """
        Create a new notification
        
        Args:
            user_id: User ID or 'all' for broadcast
            notification_type: Type of notification (program, toli, message, etc.)
            title: Notification title
            message: Notification message
            data: Additional data (optional)
        
        Returns:
            Notification ID
        """
        try:
            notification = {
                'user_id': user_id,
                'type': notification_type,
                'title': title,
                'message': message,
                'data': data or {},
                'is_read': False,
                'created_at': datetime.utcnow()
            }
            
            result = self.db.db.notifications.insert_one(notification)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error creating notification: {e}")
            return None
    
    def get_user_notifications(self, user_id, unread_only=False, limit=50):
        """Get notifications for a user"""
        try:
            query = {'$or': [{'user_id': user_id}, {'user_id': 'all'}]}
            
            if unread_only:
                query['is_read'] = False
            
            notifications = list(self.db.db.notifications.find(query)
                                .sort('created_at', -1)
                                .limit(limit))
            
            return notifications
            
        except Exception as e:
            print(f"Error getting notifications: {e}")
            return []
    
    def mark_as_read(self, notification_id):
        """Mark notification as read"""
        try:
            from bson import ObjectId
            self.db.db.notifications.update_one(
                {'_id': ObjectId(notification_id)},
                {'$set': {'is_read': True}}
            )
            return True
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False
    
    def mark_all_as_read(self, user_id):
        """Mark all notifications as read for a user"""
        try:
            self.db.db.notifications.update_many(
                {'user_id': user_id, 'is_read': False},
                {'$set': {'is_read': True}}
            )
            return True
        except Exception as e:
            print(f"Error marking all as read: {e}")
            return False
    
    def get_unread_count(self, user_id):
        """Get count of unread notifications"""
        try:
            count = self.db.db.notifications.count_documents({
                '$or': [{'user_id': user_id}, {'user_id': 'all'}],
                'is_read': False
            })
            return count
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0
    
    def delete_notification(self, notification_id):
        """Delete a notification"""
        try:
            from bson import ObjectId
            self.db.db.notifications.delete_one({'_id': ObjectId(notification_id)})
            return True
        except Exception as e:
            print(f"Error deleting notification: {e}")
            return False
    
    # Notification creators for specific events
    
    def notify_program_created(self, program_data, student_id):
        """Notify when a program is created"""
        return self.create_notification(
            user_id='admin',  # Notify all admins
            notification_type='program',
            title='New Program Created',
            message=f"New program '{program_data.get('title')}' has been created",
            data={
                'program_id': str(program_data.get('_id')),
                'student_id': student_id,
                'program_type': program_data.get('program_type')
            }
        )
    
    def notify_toli_created(self, toli_data):
        """Notify when a toli is created"""
        return self.create_notification(
            user_id='admin',
            notification_type='toli',
            title='New Toli Created',
            message=f"New toli '{toli_data.get('name')}' has been created",
            data={
                'toli_id': str(toli_data.get('_id')),
                'member_count': len(toli_data.get('members', []))
            }
        )
    
    def notify_member_added(self, toli_id, member_name):
        """Notify when a member is added to toli"""
        return self.create_notification(
            user_id='admin',
            notification_type='toli',
            title='Member Added to Toli',
            message=f"{member_name} has been added to the toli",
            data={'toli_id': toli_id}
        )
    
    def notify_message_received(self, user_id, sender_name, message_title):
        """Notify when a message is received"""
        return self.create_notification(
            user_id=user_id,
            notification_type='message',
            title='New Message',
            message=f"You have a new message from {sender_name}: {message_title}",
            data={'sender': sender_name}
        )
    
    def notify_status_change(self, user_id, entity_type, entity_name, new_status):
        """Notify when status changes"""
        return self.create_notification(
            user_id=user_id,
            notification_type='status',
            title=f'{entity_type.title()} Status Updated',
            message=f"{entity_name} status changed to {new_status}",
            data={
                'entity_type': entity_type,
                'new_status': new_status
            }
        )
    
    def broadcast_announcement(self, title, message):
        """Broadcast announcement to all users"""
        return self.create_notification(
            user_id='all',
            notification_type='announcement',
            title=title,
            message=message
        )
