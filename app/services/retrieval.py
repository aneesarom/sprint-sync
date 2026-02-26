from app.services.ai_services import embeddings_model
from app.services.supabase_client import supabase
from app.logging_config import get_logger

logger = get_logger(__name__)

def apply_rrf(profiles_list: list, weights: list = None, k: int = 60):
    logger.info("apply_rrf", info="Starting RRF")
    scores_dict = {}
    all_profiles = {}
    for profiles in profiles_list:
        for idx, profile in enumerate(profiles):
                profile_id = profile["id"]
                score = 1 / (k + idx)
                if profile_id in scores_dict:
                    if weights:
                        scores_dict[profile_id] += score * weights[idx]
                    else:
                        scores_dict[profile_id] += score
                else:
                    if weights:
                        scores_dict[profile_id] = score * weights[idx]
                    else:
                        scores_dict[profile_id] = score
                    all_profiles[profile_id] = profile
    logger.info("Finished calculating RRF", scores=scores_dict)
    sorted_profiles = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
    final_profiles = [all_profiles[profile_id] for profile_id, score in sorted_profiles]
    return final_profiles

def vector_search(user_query: str, num_profiles: int):
    logger.info("vector_search", info="Starting vector search", query=user_query)
    query_embedding = embeddings_model.embed_query(user_query)
    result = supabase.rpc('vector_search_profile', {
                'query_embedding': query_embedding,
                'match_threshold': 0.3,
                'snippets_per_search': num_profiles
            }).execute()
    if not result.data:
        logger.info("No results found for vector search", query=user_query)
    return result.data if result.data else []


def keyword_search(user_query: str, num_profiles: int):
    logger.info("Starting keyword search", query=user_query)
    result = supabase.rpc('keyword_search_profile', {
                'user_query': user_query,
                'snippets_per_search': num_profiles
            }).execute()
    if not result.data:
        logger.info("No results found for keyword search", query=user_query)
    return result.data if result.data else []


def multi_query_hybrid_search(keyword_search_queries: list, vector_search_queries: list, num_profiles):
    logger.info("Starting hybrid search", keyword_search_queries=keyword_search_queries, vector_search_queries=vector_search_queries)
    profiles_result = []
    for query in keyword_search_queries:
        profiles = keyword_search(query, num_profiles)
        profiles_result.append(profiles)
    for query in vector_search_queries:
        profiles = vector_search(query, num_profiles)
        profiles_result.append(profiles)
    relevant_profiles = apply_rrf(profiles_result)
    logger.info("Finished hybrid search", total_profiles=len(relevant_profiles))
    finalized_profiles = relevant_profiles[:num_profiles]
    return finalized_profiles