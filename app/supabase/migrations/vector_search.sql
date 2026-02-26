DROP FUNCTION IF EXISTS vector_search_profile(vector, double precision, integer);

CREATE OR REPLACE FUNCTION vector_search_profile(
    query_embedding vector,
    match_threshold double precision DEFAULT 0.3,
    snippets_per_search integer DEFAULT 10
)
RETURNS TABLE (
    id uuid,
    user_id uuid,
    profile_tasks text,
    profile_skills text,
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
        rs.embedding IS NOT NULL
        AND (1 - (rs.embedding <=> query_embedding)) > match_threshold
    ORDER BY rs.embedding <=> query_embedding
    LIMIT snippets_per_search;
$function$;