DROP FUNCTION IF EXISTS keyword_search_profile(text, integer);

CREATE OR REPLACE FUNCTION keyword_search_profile(
    user_query text,
    snippets_per_search integer DEFAULT 10
)
RETURNS TABLE (
    id uuid,
    user_id uuid,
    profile_skills text,
    profile_tasks text,
    embedding vector
)
LANGUAGE sql
AS $function$
    SELECT
        rs.id,
        rs.user_id,
        rs.profile_skills,
        rs.profile_tasks,
        rs.embedding
    FROM resumes rs
    WHERE
        rs.fts @@ to_tsquery(
            'english',
            replace(lower(user_query), ' ', ' | ')
        )
    ORDER BY
        ts_rank_cd(
            rs.fts,
            to_tsquery('english', replace(lower(user_query), ' ', ' | ')),
            32
        ) DESC
    LIMIT
        snippets_per_search;
$function$;