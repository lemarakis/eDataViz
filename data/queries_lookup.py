LOOKUP_AREAS = """
SELECT ar_id, ar_name
FROM area
ORDER BY ar_name;
"""

LOOKUP_YEARS = """
SELECT DISTINCT p_year
FROM production
WHERE p_year IS NOT NULL
ORDER BY p_year;
"""

LOOKUP_BREEDS = """
SELECT id, name
FROM breed
ORDER BY name;
"""
