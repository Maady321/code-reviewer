-- Run this schema in your Supabase SQL Editor

-- 1. Review Sessions Table
CREATE TABLE public.review_sessions (
    id uuid NOT NULL PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    repo_url text,
    commit_hash text,
    created_at timestamp with time zone DEFAULT now()
);

-- Enable Row Level Security (RLS) for user privacy
ALTER TABLE public.review_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only view their own sessions" ON public.review_sessions 
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own sessions" ON public.review_sessions 
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 2. Code Quality Scores Table
CREATE TABLE public.code_quality_scores (
    id uuid NOT NULL PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES public.review_sessions(id) ON DELETE CASCADE,
    score numeric NOT NULL,
    total_issues integer DEFAULT 0,
    critical_issues integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now()
);

-- 3. Review Results Table
CREATE TABLE public.review_results (
    id uuid NOT NULL PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES public.review_sessions(id) ON DELETE CASCADE,
    file_name text NOT NULL,
    line_number integer,
    severity text NOT NULL,
    issue_type text NOT NULL,
    description text NOT NULL,
    suggestion text,
    created_at timestamp with time zone DEFAULT now()
);

-- Note: Because scores and results are only fetched alongside the parent session (which is protected by RLS),
-- we can optionally enable RLS strictly based on their relationships. But for the backend server mapping 
-- via service-role keys (or direct execution), the operations bypass RLS.
