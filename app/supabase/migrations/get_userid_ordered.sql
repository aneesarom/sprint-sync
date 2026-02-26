CREATE OR REPLACE FUNCTION get_users_by_ids_ordered(input_ids uuid[])
RETURNS TABLE (
    id uuid,
    username text
)
LANGUAGE sql
AS $$
    SELECT u.id, u.username
    FROM users u
    WHERE u.id = ANY(input_ids)
    ORDER BY array_position(input_ids, u.id);
$$;