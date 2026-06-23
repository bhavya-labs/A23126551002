# Stage 1 – Notification System API Design

## Overview

The Campus Notification System provides real-time notifications to students regarding:

* Placements
* Events
* Results
* Announcements

## Request Headers

```http
Authorization: Bearer <JWT_TOKEN>
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

Response:

```json
{
  "message": "Notification marked as read"
}
```

### Delete Notification

```http
DELETE /api/v1/notifications/{id}
```

Response:

```json
{
  "message": "Notification deleted successfully"
}
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

---

# Stage 2 – Database Design

## Database Choice

I selected PostgreSQL for this system because notifications require reliable storage and consistent reads. PostgreSQL supports ACID transactions, powerful indexing features, and can scale efficiently as the number of users and notifications increases.

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
INSERT INTO notifications (
    notification_id,
    title,
    message,
    category,
    created_at
)
VALUES (
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

### Challenge 1: Large Notification Volume

Solutions:

* Indexing
* Pagination
* Partitioning

### Challenge 2: High Concurrent Users

Solutions:

* Redis caching
* Read replicas
* Load balancing

### Challenge 3: Database Growth

Solutions:

* Archiving old notifications
* Partitioning by date
* Periodic cleanup jobs

---

# Stage 3 – Query Performance Optimization

## Current Query

```sql
SELECT *
FROM notifications
WHERE studentID = 1042
  AND isRead = false
ORDER BY createdAt DESC;
```

## Is the Query Accurate?

The query correctly retrieves unread notifications for a specific user and sorts them by creation time in descending order. Functionally, it satisfies the requirement. However, when the notifications table grows to millions of records, performance issues can appear if the database is not properly optimized.

## Why is it Slow?

With approximately 5,000,000 notifications:

* Full table scans may occur
* Sorting becomes expensive
* `SELECT *` retrieves unnecessary columns
* No pagination limits result size

## Computational Cost

Without indexes:

```text
Filtering: O(N)
Sorting: O(K log K)
```

Where:

* N = Total notifications
* K = Matching notifications

With proper indexing:

```text
Approximately O(log N)
```

## Optimization 1: Composite Index

```sql
CREATE INDEX idx_notifications_student_read_created
ON notifications(studentID, isRead, createdAt DESC);
```

Benefits:

* Faster filtering
* Faster sorting
* Better query planning

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
* Faster response times

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

Example:

```text
notifications_2026_jan
notifications_2026_feb
notifications_2026_mar
```

Benefits:

* Smaller tables
* Faster searches
* Easier archival

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

## Should We Add Indexes on Every Column?

No.

Adding indexes on every column:

* Increases storage requirements
* Slows INSERT operations
* Slows UPDATE operations
* Slows DELETE operations
* Adds maintenance overhead

Indexes should be created only on:

* Frequently filtered columns
* Frequently joined columns
* Frequently sorted columns

Examples:

```text
studentID
isRead
createdAt
notificationType
```

## Query: Students Who Received Placement Notifications in Last 7 Days

```sql
SELECT DISTINCT studentID
FROM notifications
WHERE notificationType = 'Placement'
  AND createdAt >= NOW() - INTERVAL '7 days';
```

---

# Stage 4 – Reducing Database Load

## Problem Statement

Currently, notifications are fetched from the database on every page load.

Flow:

```text
Student Opens Page
↓
API Request
↓
Database Query
↓
Response
```

With 50,000 students this creates heavy database traffic.

## Solution 1: Redis Cache

Store frequently accessed notifications and unread counts in Redis.

Flow:

```text
Request
↓
Redis Cache
↓
Database (Only on Cache Miss)
```

### Benefits

* Sub-millisecond reads
* Reduced database load
* Faster page rendering

### Tradeoffs

* Cache invalidation complexity
* Additional infrastructure

## Solution 2: WebSocket-Based Push Notifications

Flow:

```text
Notification Created
↓
Notification Service
↓
WebSocket Server
↓
Connected Students
```

### Benefits

* Real-time delivery
* Eliminates frequent polling
* Lower database load

### Tradeoffs

* Persistent connections consume memory
* More complex infrastructure

## Solution 3: Pagination

```sql
SELECT *
FROM notifications
WHERE studentID = 1042
ORDER BY createdAt DESC
LIMIT 20;
```

### Benefits

* Smaller payloads
* Reduced memory usage
* Faster API responses

## Stage 4 – Reducing Database Load
Problem Statement

In the current design, every time a student opens the notification page, the application sends a request to the database. This approach works well for small numbers of users but becomes expensive when thousands of students access the system simultaneously.

A typical request flow is:

Student Opens Page
        |
        v
API Request
        |
        v
Database Query
        |
        v
Response

With approximately 50,000 students, continuously querying the database for the same information can lead to increased response times and unnecessary database load.

# Stage 5 – Reliable and Scalable Bulk Notification Delivery

## Problems with the Current Implementation

Current implementation:

```text
function notify_all(student_ids, message):
    for student_id in student_ids:
        send_email(student_id, message)
        save_to_db(student_id, message)
        push_to_app(student_id, message)
```

### Shortcomings

1. Sequential processing is slow.

   * Sending notifications to 50,000 students one by one can take several minutes.

2. Single point of failure.

   * If `send_email()` fails for one student, the entire process may stop.

3. No retry mechanism.

   * Temporary email service failures can cause permanent notification loss.

4. Poor scalability.

   * One application server cannot efficiently process 50,000 requests sequentially.

5. Tight coupling.

   * Email delivery, database storage, and push notifications are dependent on each other.

6. No fault tolerance.

   * Failures are difficult to recover from.

---

## What if send_email() Failed for 200 Students?

The failed students should not lose notifications.

Recommended approach:

1. Store the notification in the database first.
2. Track delivery status.
3. Push failed email requests into a retry queue.
4. Retry automatically using background workers.
5. Log all failures for monitoring and auditing.

Example:

```text
Email Status:
PENDING
SENT
FAILED
RETRYING
```

This ensures reliable delivery even if external email services experience outages.

---

## Should Saving to DB and Sending Email Happen Together?

No.

Database writes and email delivery should be decoupled.

Reasons:

* Database operations are usually fast and reliable.
* Email services are external systems and may fail.
* Coupling both operations increases response time.
* A failed email should not prevent notification creation.

Recommended Flow:

```text
Create Notification
        |
        v
Save Notification To Database
        |
        v
Publish Event To Queue
        |
        +----------------+
        |                |
        v                v
 Email Worker      Push Worker
```

---

## Recommended Architecture

Components:

* Notification Service
* PostgreSQL Database
* Message Queue (Kafka/RabbitMQ)
* Email Workers
* Push Notification Workers
* Redis Cache

Architecture:

```text
HR Clicks Notify All
          |
          v
 Notification Service
          |
          v
 Save Notification To DB
          |
          v
     Message Queue
      /         \
     /           \
Email Worker   Push Worker
     |             |
     v             v
 Email API    WebSocket Server
```

Benefits:

* High throughput
* Fault tolerance
* Independent scaling
* Retry capability
* Faster user experience

---

## Revised Pseudocode

```text
function notify_all(student_ids, message):

    notification_id = save_notification(message)

    for student_id in student_ids:

        create_user_notification(
            notification_id,
            student_id,
            status="PENDING"
        )

        publish_to_queue(
            notification_id,
            student_id,
            message
        )


worker email_worker():

    while true:

        job = consume_queue()

        try:
            send_email(job.student_id, job.message)
            mark_email_status(job.student_id, "SENT")

        except Exception:
            mark_email_status(job.student_id, "FAILED")
            retry(job)


worker push_worker():

    while true:

        job = consume_queue()

        try:
            push_to_app(job.student_id, job.message)
            mark_push_status(job.student_id, "SENT")

        except Exception:
            mark_push_status(job.student_id, "FAILED")
            retry(job)
```

---

## Final Recommendation

Use an asynchronous event-driven architecture with:

* PostgreSQL for persistence
* Kafka or RabbitMQ for message queuing
* Redis for caching
* Background workers for email and push delivery
* Automatic retry mechanisms

This design can reliably handle notifications for 50,000+ students while maintaining high availability and fault tolerance.

