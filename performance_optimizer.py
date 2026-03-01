"""
Performance Optimization Module for AI HR Agent
Provides caching, parallel processing, and batch operations
"""

import streamlit as st
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import hashlib
import json
import time
from typing import List, Dict, Any, Tuple
import asyncio
from threading import Lock

class PerformanceOptimizer:
    """
    Centralized performance optimization for HR Agent
    """
    
    def __init__(self):
        self.cache_lock = Lock()
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize Streamlit session state for caching"""
        if 'data_cache' not in st.session_state:
            st.session_state.data_cache = {}
        if 'processed_candidates' not in st.session_state:
            st.session_state.processed_candidates = {}
        if 'llm_cache' not in st.session_state:
            st.session_state.llm_cache = {}
    
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def load_dataset_cached(file_path: str) -> pd.DataFrame:
        """Cached data loading with Streamlit cache"""
        return pd.read_csv(file_path)
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def preprocess_candidates_cached(df: pd.DataFrame) -> List[Dict]:
        """Preprocess candidates with caching"""
        candidates_data = []
        
        for idx, row in df.iterrows():
            skills_raw = str(row.get("Skills", ""))
            skills_list = [s.strip().lower() for s in skills_raw.split(",") if s.strip()]
            
            candidate_data = {
                'candidate_id': str(idx),
                'name': row.get("Name", f"Candidate_{idx}"),
                'email': f"user{idx}@example.com",
                'resume_text': f"{row.get('Current_Job_Title','')} {skills_raw}",
                'skills': skills_list,
                'experience_years': float(row.get("Experience_Years", 0)),
                'status': "applied",
                # Pre-compute skill sets for faster matching
                'skills_set': set(skills_list),
                'resume_hash': hashlib.md5(f"{row.get('Current_Job_Title','')} {skills_raw}".encode()).hexdigest()
            }
            candidates_data.append(candidate_data)
        
        return candidates_data
    
    def batch_semantic_matching(self, candidates: List[Any], jd: Any, llm_agent: Any, batch_size: int = 50) -> Dict[str, float]:
        """
        Batch process semantic matching with intelligent caching
        """
        semantic_scores = {}
        
        # Group candidates into batches
        batches = [candidates[i:i + batch_size] for i in range(0, len(candidates), batch_size)]
        
        with st.progress(0) as progress_bar:
            for batch_idx, batch in enumerate(batches):
                # Check cache first
                uncached_candidates = []
                for candidate in batch:
                    cache_key = f"semantic_{candidate.candidate_id}_{jd.job_id}"
                    if cache_key in st.session_state.llm_cache:
                        semantic_scores[candidate.candidate_id] = st.session_state.llm_cache[cache_key]
                    else:
                        uncached_candidates.append(candidate)
                
                # Process uncached candidates in parallel
                if uncached_candidates:
                    batch_scores = self._parallel_semantic_matching(uncached_candidates, jd, llm_agent)
                    
                    # Update cache and results
                    for candidate_id, score in batch_scores.items():
                        cache_key = f"semantic_{candidate_id}_{jd.job_id}"
                        st.session_state.llm_cache[cache_key] = score
                        semantic_scores[candidate_id] = score
                
                # Update progress
                progress = (batch_idx + 1) / len(batches)
                progress_bar.progress(progress)
        
        return semantic_scores
    
    def _parallel_semantic_matching(self, candidates: List[Any], jd: Any, llm_agent: Any) -> Dict[str, float]:
        """
        Parallel processing of semantic matching for a batch
        """
        semantic_scores = {}
        
        def process_candidate(candidate):
            try:
                semantic_result = llm_agent.match_resume_to_job(
                    candidate.resume_text[:1000], 
                    jd.description[:500]
                )
                if semantic_result["success"]:
                    content = json.loads(semantic_result["content"]) if isinstance(semantic_result["content"], str) else semantic_result["content"]
                    semantic_score = content.get("match_score", 0.0)
                    return candidate.candidate_id, min(semantic_score * 0.1, 0.1)
            except Exception as e:
                st.warning(f"Semantic matching failed for {candidate.candidate_id}: {e}")
            return candidate.candidate_id, 0.0
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_candidate = {executor.submit(process_candidate, candidate): candidate for candidate in candidates}
            
            for future in as_completed(future_to_candidate):
                candidate_id, score = future.result()
                semantic_scores[candidate_id] = score
        
        return semantic_scores
    
    def vectorized_skill_matching(self, candidates_data: List[Dict], required_skills: set, preferred_skills: set) -> np.ndarray:
        """
        Vectorized skill matching using numpy for speed
        """
        n_candidates = len(candidates_data)
        n_required = len(required_skills)
        n_preferred = len(preferred_skills)
        
        # Pre-compute skill matches
        required_matches = np.zeros(n_candidates)
        preferred_matches = np.zeros(n_candidates)
        
        for i, candidate in enumerate(candidates_data):
            candidate_skills = candidate['skills_set']
            required_matches[i] = len(required_skills & candidate_skills)
            preferred_matches[i] = len(preferred_skills & candidate_skills)
        
        # Vectorized score calculation
        skill_scores = required_matches / n_required if n_required > 0 else np.ones(n_candidates)
        preferred_scores = preferred_matches / n_preferred if n_preferred > 0 else np.zeros(n_candidates)
        
        return skill_scores, preferred_scores
    
    def batch_question_generation(self, shortlisted_candidates: List[Any], jd: Any, question_generator: Any) -> Dict[str, List[Dict]]:
        """
        Batch generate interview questions with caching
        """
        questions_map = {}
        
        # Check cache first
        uncached_candidates = []
        for candidate in shortlisted_candidates:
            cache_key = f"questions_{candidate.candidate_id}_{jd.job_id}"
            if cache_key in st.session_state.llm_cache:
                questions_map[candidate.candidate_id] = st.session_state.llm_cache[cache_key]
            else:
                uncached_candidates.append(candidate)
        
        # Generate questions for uncached candidates
        if uncached_candidates:
            with st.spinner(f"Generating questions for {len(uncached_candidates)} candidates..."):
                for candidate in uncached_candidates:
                    try:
                        questions = question_generator.generate_questions(candidate, jd)
                        cache_key = f"questions_{candidate.candidate_id}_{jd.job_id}"
                        st.session_state.llm_cache[cache_key] = questions
                        questions_map[candidate.candidate_id] = questions
                    except Exception as e:
                        st.warning(f"Question generation failed for {candidate.name}: {e}")
                        questions_map[candidate.candidate_id] = []
        
        return questions_map


class StreamlitStateManager:
    """
    Manages Streamlit state to avoid unnecessary reruns
    """
    
    @staticmethod
    def get_or_compute(key: str, compute_func, *args, **kwargs):
        """
        Get from session state or compute and store
        """
        if key not in st.session_state:
            with st.spinner(f"Computing {key}..."):
                st.session_state[key] = compute_func(*args, **kwargs)
        return st.session_state[key]
    
    @staticmethod
    def invalidate_cache(pattern: str = None):
        """
        Invalidate cached data matching pattern
        """
        if pattern:
            keys_to_remove = [k for k in st.session_state.keys() if pattern in k]
            for key in keys_to_remove:
                del st.session_state[key]
        else:
            # Clear all cache
            for key in ['data_cache', 'processed_candidates', 'llm_cache']:
                if key in st.session_state:
                    st.session_state[key] = {}


class LazyUIRenderer:
    """
    Lazy rendering for large datasets
    """
    
    @staticmethod
    def paginated_results(candidates: List[Any], page_size: int = 10):
        """
        Paginated display of candidates
        """
        total_pages = (len(candidates) + page_size - 1) // page_size
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.selectbox(
                "Page", 
                range(1, total_pages + 1), 
                format_func=lambda x: f"Page {x} of {total_pages}"
            )
        
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(candidates))
        
        return candidates[start_idx:end_idx], page, total_pages
    
    @staticmethod
    def progressive_loading(candidates: List[Any], initial_count: int = 5):
        """
        Progressive loading with "Load More" button
        """
        if 'display_count' not in st.session_state:
            st.session_state.display_count = initial_count
        
        display_candidates = candidates[:st.session_state.display_count]
        
        if st.session_state.display_count < len(candidates):
            if st.button(f"Load More ({len(candidates) - st.session_state.display_count} remaining)"):
                st.session_state.display_count = min(
                    st.session_state.display_count + initial_count, 
                    len(candidates)
                )
                st.rerun()
        
        return display_candidates


# Performance monitoring decorator
def monitor_performance(func):
    """Decorator to monitor function performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Store performance metrics in session state
        if 'performance_metrics' not in st.session_state:
            st.session_state.performance_metrics = {}
        
        st.session_state.performance_metrics[func.__name__] = {
            'duration': end_time - start_time,
            'timestamp': time.time()
        }
        
        return result
    return wrapper