DROP TABLE IF EXISTS resume_snippets CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Users table
CREATE TABLE users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    username text UNIQUE NOT NULL,
    email text UNIQUE NOT NULL,
    password text NOT NULL,
    is_admin boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


-- Tasks table
CREATE TABLE tasks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES users(id) ON DELETE SET NULL,
    title text NOT NULL,
    description text,
    status text NOT NULL 
        CHECK (status IN ('created', 'assigned', 'in_process', 'completed')) 
        DEFAULT 'created',
    total_minutes float DEFAULT 0.0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


-- Resume snippets table (Vector + FTS hybrid search)
CREATE TABLE resumes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    profile_skills text NOT NULL,
    profile_tasks text NOT NULL,
    s3_key text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    fts tsvector GENERATED ALWAYS AS (to_tsvector('english', profile_skills)) STORED,
    embedding vector(768) NOT NULL
);

-- Indexes
CREATE INDEX resume_profile_skills_fts_idx 
ON resumes USING gin (fts);

CREATE INDEX resume_profile_embedding_hnsw_idx 
ON resumes USING hnsw (embedding vector_cosine_ops);