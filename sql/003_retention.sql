-- =================================================================
-- Parent2Parent — Retention job (run on EACH shard)
-- =================================================================
-- Keeps chat_message_log from growing forever. Default retention is
-- 14 days, which is plenty of runway for the CEO to review flags
-- without the audit table becoming a second "live chat" store.
-- Pair this with a Supabase Cron schedule (Dashboard > Database >
-- Cron Jobs) calling select public.purge_old_chat_logs(); once a day.
-- =================================================================

create or replace function public.purge_old_chat_logs(retention_days int default 14)
returns void language plpgsql as $$
begin
    delete from public.chat_message_log
    where created_at < now() - (retention_days || ' days')::interval
      and id not in (
          select chat_message_log_id from public.moderation_flags
          where chat_message_log_id is not null and status = 'open'
      );

    delete from public.verification_codes
    where expires_at < now() - interval '1 day';
end;
$$;

-- Example cron registration (run manually once in the SQL editor,
-- requires the pg_cron extension which Supabase provides):
-- select cron.schedule('purge-chat-logs-daily', '0 4 * * *', $$select public.purge_old_chat_logs();$$);
