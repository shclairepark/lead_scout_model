import numpy as np

# ===================================
# Embedding Similarity Functions
# ===================================

def dot_product(vec1, vec2):
    """
    Calculate dot product between two vectors
    
    Args:
        vec1: numpy array or list, shape (d,)
        vec2: numpy array or list, shape (d,)
    
    Returns:
        score: float (sum of element-wise products)
    
    Example:
        vec1 = [1, 2, 3]
        vec2 = [4, 5, 6]
        result = 1*4 + 2*5 + 3*6 = 32
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    return np.dot(vec1, vec2)


def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors

    Args:
        vec1: numpy array or list, shape (d,)
        vec2: numpy array or list, shape (d,)
    
    Returns:
        similarity: float in range [-1, 1]
    
    Example:
        vec1 = [1, 0, 0]
        vec2 = [1, 0, 0]
        result = 1.0 (identical)
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    # Formula:
    #     cosine_sim = dot(vec1, vec2) / (||vec1|| * ||vec2||)
    #     where ||vec|| = sqrt(sum(vec^2))
    # Edge case: Handle division by zero if magnitude is 0 -> add epsilon to the denominator
    epsilon = 1e-8
    cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + epsilon) 
    return cosine_sim


def euclidean_distance(vec1, vec2):
    """
    Calculate Euclidean distance between two vectors
    
    Args:
        vec1: numpy array or list, shape (d,)
        vec2: numpy array or list, shape (d,)
    
    Returns:
        distance: float (>= 0)
    
    Example:
        vec1 = [0, 0, 0]
        vec2 = [3, 4, 0]
        result = 5.0 (3-4-5 triangle)
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    # Formula:
    #     distance = sqrt(sum((vec1 - vec2)^2))
    distance = np.sqrt(np.sum(np.square(vec1 - vec2)))
    return distance