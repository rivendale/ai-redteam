# Proposal: a daily bike-health sheet

## 1. The problem
Riders report stuck bikes (a lock that will not release, a dead battery) about 14 times a week. We want that number lower.

## 2. What we have already
Every bike reports its battery level, lock state and last-seen time to the ops dashboard every 5 minutes. The dashboard already shows a bike as "stuck" when its lock
state has not changed for 3 hours after a rider unlocked it.

## 3. The proposal
Every morning each dock technician fills in a 40-column bike-health sheet for every bike at their stations, by hand (about 25 minutes per technician per day, 22 technicians).
The sheets are collected on Friday and one analyst builds the weekly stuck-bike report from them. Complaints will fall because the report exists.

## 4. Cost
22 technicians x 25 minutes x 5 days is about 46 hours a week of technician time. No software cost.
