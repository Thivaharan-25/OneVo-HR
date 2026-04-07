# User Management — End-to-End Logic

**Module:** Infrastructure
**Feature:** User Management

---

## Create User

### Flow

```
POST /api/v1/users
  -> UserController.Create(CreateUserCommand)
    -> [RequirePermission("users:manage")]
    -> UserService.CreateUserAsync(command, ct)
      -> 1. Validate email unique within tenant
      -> 2. Hash password via bcrypt
      -> 3. INSERT into users
         -> is_active = true, email_verified = false
      -> 4. Send verification email via notifications
      -> 5. Log to audit_logs
      -> Return Result.Success(userDto)
```

## Users vs Employees

- **users** = login identity (email, password_hash)
- **employees** = HR identity (name, department, salary)
- Linked 1:1 via `user_id` on employees table
- When working with HR features, always query through employees

## Related

- [[user-management|Overview]]
- [[tenant-management]]
- [[authentication]]
- [[authorization]]
- [[audit-logging]]
- [[event-catalog]]
- [[error-handling]]
