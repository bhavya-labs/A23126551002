# Stage 1 – Notification System API Design

## Overview

The Campus Notification System provides real-time notifications to students regarding:

* Placements
* Events
* Results
* Announcements

## Request Headers

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJhbGFrdW50YWJoYXZ5YS4yMy5jc2RAYW5pdHMuZWR1LmluIiwiZXhwIjoxNzgyMTk1NDk1LCJpYXQiOjE3ODIxOTQ1OTUsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiJmZWRkMzE4Yy04YTZlLTQzMzctOTYyNi0zN2ExMjMzYTQyNGYiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJhbGFrdW50YSBiaGF2eWEiLCJzdWIiOiI0YTg3NmNjZC1kMDUwLTQ4NjgtOGI0MS1iN2IzNzMzZDJhNDcifSwiZW1haWwiOiJhbGFrdW50YWJoYXZ5YS4yMy5jc2RAYW5pdHMuZWR1LmluIiwibmFtZSI6ImFsYWt1bnRhIGJoYXZ5YSIsInJvbGxObyI6ImEyMzEyNjU1MTAwMiIsImFjY2Vzc0NvZGUiOiJNVHF4YXIiLCJjbGllbnRJRCI6IjRhODc2Y2NkLWQwNTAtNDg2OC04YjQxLWI3YjM3MzNkMmE0NyIsImNsaWVudFNlY3JldCI6IldjcXpxSmp1UkRkZUZwZ3YifQ.r3brxj2Lku3buAXw_3x3ik4-tGeLFlphddZoan72Raw
Content-Type: application/json
Accept: application/json
```

## API Endpoints

### Get Notifications

```http
GET /api/v1/notifications
```

Sample Response:

```json
{
  "notifications": [
    {
      "ID": "ca64d61b-4808-42e8-989b-dd5f89ff4eeb",
      "Type": "Placement",
      "Message": "Tesla Inc. hiring",
      "Timestamp": "2026-06-22 13:04:13"
    },
    {
      "ID": "5c3e9c15-96ab-4b6e-b531-8aa2aa762299",
      "Type": "Event",
      "Message": "cult-fest",
      "Timestamp": "2026-06-22 08:34:00"
    }
  ]
}
```

### Create Notification

```http
POST /api/v1/notifications
```

Request:

```json
{
  "title": "Tesla Hiring",
  "message": "Tesla Inc. hiring",
  "category": "PLACEMENT"
}
```

Response:

```json
{
  "message": "Notification created successfully"
}
```

### Mark Notification as Read

```http
PATCH /api/v1/notifications/{id}/read
```

### Delete Notification

```http
DELETE /api/v1/notifications/{id}
```

## Real-Time Notification Mechanism

Use WebSocket for instant notification delivery.

```http
ws://domain/api/v1/notifications/ws
```

Example Event:

```json
{
  "event": "NEW_NOTIFICATION",
  "data": {
    "title": "Tesla Hiring",
    "message": "Tesla Inc. hiring"
  }
}
```

# Stage 2 – Database Design

## Database Choice

PostgreSQL is chosen because it provides:

* ACID compliance
* Efficient indexing
* Strong consistency
* High scalability

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150) UNIQUE
);
```

### Notifications Table

```sql
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY,
    title VARCHAR(255),
    message TEXT,
    category VARCHAR(50),
    created_at TIMESTAMP
);
```

### User Notifications Table

```sql
CREATE TABLE user_notifications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    notification_id UUID REFERENCES notifications(notification_id),
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP
);
```

## Sample Queries

### Create Notification

```sql
INSERT INTO notifications(
notification_id,
title,
message,
category,
created_at
)
VALUES(
gen_random_uuid(),
'Tesla Hiring',
'Tesla Inc. hiring',
'PLACEMENT',
NOW()
);
```

### Get Notifications

```sql
SELECT n.*, un.is_read
FROM notifications n
JOIN user_notifications un
ON n.notification_id = un.notification_id
WHERE un.user_id = $1
ORDER BY n.created_at DESC;
```

### Mark Notification Read

```sql
UPDATE user_notifications
SET is_read = TRUE,
    read_at = NOW()
WHERE user_id = $1
AND notification_id = $2;
```

## Scaling Challenges

* Large notification volume
* High concurrent users
* Database growth

Solutions:

* Indexing
* Pagination
* Redis caching
* Database partitioning

# Stage 3 – Query Performance Optimization

## Problem Analysis

Current Query:

```sql
SELECT *
FROM notifications
WHERE studentID = 1042
  AND isRead = false
ORDER BY createdAt DESC;
```

Problems:

* Full table scans
* Expensive sorting
* Slow response for millions of records

## Optimization 1: Composite Index

```sql
CREATE INDEX idx_notifications_student_read_created
ON notifications(studentID, isRead, createdAt DESC);
```

Benefits:

* Faster filtering
* Faster sorting
* Better index utilization

## Optimization 2: Pagination

```sql
SELECT *
FROM notifications
WHERE studentID = 1042
  AND isRead = false
ORDER BY createdAt DESC
LIMIT 20 OFFSET 0;
```

Benefits:

* Reduced memory usage
* Faster API response

## Optimization 3: Keyset Pagination

```sql
SELECT *
FROM notifications
WHERE studentID = 1042
  AND isRead = false
  AND createdAt < '2026-06-23 10:00:00'
ORDER BY createdAt DESC
LIMIT 20;
```

Benefits:

* Better scalability
* Faster than OFFSET pagination

## Optimization 4: Partitioning

Partition notifications by date:

```text
notifications_2026_jan
notifications_2026_feb
notifications_2026_mar
```

Benefits:

* Smaller tables
* Faster queries

## Optimization 5: Redis Cache

Example:

```text
Key: unread_count:1042
Value: 15
```

Benefits:

* Reduced database load
* Faster dashboard response

## Optimized Query

```sql
SELECT notification_id,
       title,
       message,
       createdAt
FROM notifications
WHERE studentID = 1042
  AND isRead = false
ORDER BY createdAt DESC
LIMIT 20;
```
