# Notification Channels — End-to-End Logic

**Module:** Notifications
**Feature:** Notification Channels

---

## Configure Channel

### Flow

```
Channel configuration via shared-platform notification_channels table:
  -> Admin configures: email (Resend API key), Slack (webhook URL), push (FCM)
  -> Credentials encrypted via IEncryptionService
```

## Send Notification

### Flow

```
INotificationService.SendAsync(command)
  -> 1. Determine channels for event type
  -> 2. For each active channel:
     -> Email: Resend API call with rendered template
     -> In-App: INSERT into user notifications + SignalR push
     -> Slack: POST to webhook URL
  -> 3. Track delivery status
```

## Get User Notifications

### Flow

```
GET /api/v1/notifications
  -> NotificationController.List()
    -> [RequirePermission("notifications:read")]
    -> NotificationService.GetUnreadAsync(userId, ct)
      -> Query in-app notifications WHERE user_id AND is_read = false
      -> Return Result.Success(notificationDtos)
```

## Related

- [[notifications/notification-channels/overview|Notification Channels Overview]]
- [[notifications/notification-templates/overview|Notification Templates]]
- [[notifications/signalr-real-time/overview|SignalR Real-Time]]
- [[event-catalog]]
- [[error-handling]]
