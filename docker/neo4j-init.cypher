create constraint user_id_unique if not exists for (u:User) require u.id is unique;

create constraint account_id_unique if not exists for (a:Account) require a.id is unique;

create constraint txn_id_unique if not exists for (t:Transaction) require t.id is unique;

create constraint device_id_unique if not exists for (d:Device) require d.fingerprint is unique;

create constraint ip_unique if not exists for (ip:IpAddress) require ip.address is unique;

create index txn_timestamp if not exists for (t:Transaction) on (t.timestamp);

create index transfer_amount if not exists for ()-[r:TRANSFERRED_TO]-() on (r.amount);

create index user_risk if not exists for (u:User) on (u.risk_score);

