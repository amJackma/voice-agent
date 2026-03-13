# Mock Interview preparation Proxy (Voice-enabled)

This repository implements a minimal interview/mock-interviewer web app.

See `backend/README.md` and `frontend/README.md` for run instructions.

first you need to feel all your details -

<img width="352" height="439" alt="image" src="https://github.com/user-attachments/assets/33469ff7-d189-4354-b999-be0100cbd45d" />


here your interview begain ...............................!

<img width="960" height="944" alt="image" src="https://github.com/user-attachments/assets/fa69a32a-b1a5-4346-8a0f-7135888a5815" />

Technical Summary — Sourcing Manager Notification System
Problem Reframe
The dataset is not a reporting problem. It is an event stream. Every change to what needs to be ordered and by how much is an event. The job of this system is to detect those events reliably, match them against per-manager rules deterministically, and deliver them without duplicates, without missed changes, and without manual intervention.

Three concerns, kept strictly separate: detection, routing, delivery.

Architecture

Dataset CRUD API (FastAPI)
        │
        ▼
dataset_change_log          ← append-only, every field-level change written here
        │
        ▼
Celery Beat (poll every 2 min)
        │
        ▼
Subscription Engine         ← pure function: change + rules → list of managers to notify
        │
        ▼
Notification Task (Celery)  ← idempotency check → route to IMMEDIATE or DIGEST queue
        │
      ┌─┴──────────────┐
      ▼                ▼
Twilio SMS          Email (SendGrid)
      │
      ▼
notifications_sent          ← delivery receipt, Twilio SID, status, error if failed
Data Model (Five Tables)
procurement_items — the live dataset. Fields: SKU, name, category, subcategory, quantity needed, quantity on hand, reorder point, unit cost, supplier, priority tier (LOW / MED / HIGH / CRITICAL), assigned manager, last updated timestamp.

sourcing_managers — one row per manager. Fields: name, email, phone, timezone, notification preference (IMMEDIATE / DIGEST / BOTH), digest interval in minutes.

manager_subscriptions — the rules engine. Each row is one subscription rule for one manager. Filter type options: CATEGORY, SUBCATEGORY, SKU prefix, PRIORITY tier, QUANTITY THRESHOLD. Notify-on options: ALL CHANGES, QUANTITY INCREASE, QUANTITY DECREASE, THRESHOLD BREACH. Adding a new manager or a new rule is one INSERT — zero code changes, zero deployments.

dataset_change_log — append-only audit table. Every field-level change writes a row: item ID, field changed, old value, new value, who changed it, timestamp, and a processed flag. This is the source of truth for the notification pipeline and the replay source if anything fails.

notifications_sent — idempotency and observability table. Every dispatched notification writes a row with an idempotency key (hash(manager_id + change_log_id + channel)), Twilio message SID, delivery status, and any error message. This is how you answer "why didn't Manager X get notified" in under 30 seconds.

Tech Stack and Rationale
Component	Technology	Why
API layer	FastAPI	Async-native, typed, fast to instrument
Database	PostgreSQL	Change log, subscriptions, audit — relational integrity matters here
Cache + broker	Redis	Celery broker, idempotency dedup cache
Task queue	Celery + Celery Beat	Async dispatch, scheduled polling, horizontal scale, DLQ on failure
SMS	Twilio	Production delivery receipts, status callbacks, not a demo tool
Email digest	SendGrid	Reliable bulk delivery with open tracking
Logging	structlog	Structured JSON logs, searchable by manager ID or change ID
Migrations	Alembic	Schema versioning, not raw DDL
Local services	Docker Compose	PostgreSQL + Redis, no local installs bleeding into the project
No AI stack. Every component is a production-proven tool with known failure modes.

The Three Core Design Decisions
1. Change log over DB triggers DB triggers are hard to test, invisible to application observability, and couple the database to business logic. An append-only change log written by the application layer is auditable, replayable, and survives broker restarts. If Twilio goes down for 20 minutes, no changes are lost — they sit unprocessed in the log and get picked up on the next poll cycle.

2. Subscription rules in the database, not in code The rubric asks how the solution handles growth and how it stays maintainable. The answer is that adding Manager 6 with new category assignments is one INSERT into manager_subscriptions. No code change, no deployment, no PR. The subscription engine is a pure function that reads rules at runtime and evaluates them against each change.

3. Idempotency on every notification dispatch Celery retries are a real production event. Without idempotency, a Twilio timeout causes a duplicate SMS. Every notification task computes a deterministic key before calling Twilio, checks the notifications_sent table, and skips if already dispatched. This makes the entire delivery pipeline safe to retry unconditionally.

Notification Routing Logic
When a change is detected, the subscription engine evaluates it against every active subscription rule. If a match is found:

CRITICAL priority items → bypass the queue, dispatch Twilio SMS immediately
HIGH priority items → IMMEDIATE channel per manager preference
MED / LOW priority items → DIGEST queue, batched per manager on their configured interval (default 30 minutes)
A manager subscribed to "all CATEGORY=Packaging changes" and "all THRESHOLD BREACH events" gets exactly those notifications and nothing else. If a single change matches two of their own rules, they receive one notification — deduplication handled by the idempotency key.

Observability
Three questions the system can answer at any time without digging through logs:

What changed in the dataset and when? → query dataset_change_log
Who was supposed to be notified and was it sent? → join dataset_change_log + notifications_sent
Did Twilio actually deliver it? → notifications_sent.twilio_sid + Twilio status callback updating the row
Structured logs on every task execution include manager ID, change log ID, subscription rule ID, and dispatch outcome. A single log line tells you the full story of one notification.

Scalability Path
More managers — one INSERT per manager, one INSERT per subscription rule. No code changes.

Larger datasets — Celery workers scale horizontally. The poll query on dataset_change_log hits an indexed processed = false flag. At very high volume, EventBridge or SQS replaces the polling loop with push-based event fanout — the subscription engine and delivery layer do not change.

More channels — the notification task routes by channel enum. Adding Slack or webhook is one new elif branch in the dispatcher and one new value in the manager preference table.

More granular rules — adding a new filter type (e.g., SUPPLIER or COST DELTA THRESHOLD) is a new row type in manager_subscriptions and one new evaluation branch in the subscription engine. The rest of the system is unaffected.

What This Is Not
This system deliberately does not use an LLM, a vector database, or any AI layer. The problem does not require one. Relevance filtering here is deterministic — a manager either subscribes to a category or they do not. Adding AI to this would add latency, cost, and opacity to a problem that is cleanly solved by relational rules. The senior decision is knowing when not to use AI.


On Fri, Mar 13, 2026 at 1:11 PM Pranav Vijay Chand <pranav.c@myitjobmails.com> wrote:
Hi Tushar,

Below are the details :

Interview Agenda (45 minutes)
2–3 minutes: Intro and overview of the role
Case study / project walkthrough: Walk through what you did (tool + approach)
Behavioral questions
Few minuets at the end for your questions

Problem Statement: We have a dynamic dataset around what we need to order and how much that is frequently changed and causing problems for a group of five sourcing managers. Currently, these managers are either notified manually via chat or must proactively check the dataset themselves to find the information they need.

Assignment: Design a scalable, automated solution that ensures each sourcing manager receives timely and relevant updates from the dataset, minimizing manual intervention and maximizing efficiency. Your solution should address:
How will you automate the notification and information delivery process?
How will your approach handle growth (e.g., more managers, larger datasets)?
How will you ensure each manager receives only the information relevant to them but also captures all changes?
How will you ensure the solution is easy to maintain and adapt as requirements change?
The expectation is that you will show the tool and your thought process for how you built it
