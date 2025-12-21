DATA_PRODUCTION = """
SELECT 
    p_year,
    AVG(p_fdays) AS avg_days,
    AVG(p_fmilk/1000) AS avg_milk,
    STD(p_fmilk/1000) AS std_milk,
    STD(p_fdays) AS std_days,
    STD(p_males + p_females) AS std_births,
    COUNT(p_bdate) AS count_births,
    AVG(p_males + p_females) AS avg_births
FROM production 
JOIN herds ON production.p_herd_id = herds.h_id
WHERE 1=1
  AND herds.h_breed_id = %(breed)s
  AND production.p_lact BETWEEN %(lact_from)s AND %(lact_to)s
  AND production.p_fdays >= %(min_days)s
GROUP BY p_year
ORDER BY p_year;
"""

DATA_PRODUCTION_TOTAL = """
SELECT 
    AVG(p_fdays) AS avg_days,
    AVG(p_fmilk/1000) AS avg_milk,
    STD(p_fmilk/1000) AS std_milk,
    STD(p_fdays) AS std_days,
    STD(p_males + p_females) AS std_births,
    COUNT(p_bdate) AS total_births,
    AVG(p_males + p_females) AS avg_poly,
    COUNT(DISTINCT p_year) AS total_years
FROM production 
JOIN herds ON production.p_herd_id = herds.h_id
WHERE herds.h_breed_id = %(breed)s
  AND production.p_lact BETWEEN %(lact_from)s AND %(lact_to)s
  AND production.p_fdays >= %(min_days)s;
"""

DATA_CLASSIFICATION="""
SELECT
    FLOOR(p_fmilk / 50000) AS class_no,
    CONCAT(
        FLOOR(p_fmilk / 50000) * 50 + 1, ' - ',
        (FLOOR(p_fmilk / 50000) + 1) * 50
    ) AS class_range,
    COUNT(*) AS total_animals,
    AVG(p_fdays) AS avg_days,
    AVG(p_fmilk / 1000) AS avg_milk_kg,
    STD(p_fmilk / 1000) AS std_milk_kg
FROM production
JOIN herds ON production.p_herd_id = herds.h_id
WHERE herds.h_breed_id = %(breed)s
  AND p_fmilk IS NOT NULL
  AND p_lact BETWEEN %(lact_from)s AND %(lact_to)s
  AND p_year BETWEEN %(year_from)s AND %(year_to)s
GROUP BY class_no
ORDER BY class_no;
"""

DATA_PRODUCTION_MONTH="""
SELECT 
    month(p_bdate) AS month_bdate,
    Avg(p_fdays) AS avg_days,
    Avg(p_fmilk/1000) AS avg_milk,
    StD(p_fmilk/1000) AS std_milk,
    StD(p_fdays) AS std_days, 
    StD(p_males+p_females) AS std_births,
    Count(p_bdate) AS count_births,
    Avg(p_males+p_females) AS avg_births
FROM production INNER JOIN herds ON production.p_herd_id = herds.h_id 
WHERE 1=1 
    AND production.p_lact BETWEEN %(lact_from)s AND %(lact_to)s
    AND p_year BETWEEN %(year_from)s AND %(year_to)s
    AND h_breed_id=%(breed)s  
GROUP BY month(p_bdate)
"""

DATA_PRODUCTION_LACT = """
SELECT 
    p_lact,
    AVG(p_fdays) AS avg_days,
    AVG(p_fmilk/1000) AS avg_milk,
    STD(p_fmilk/1000) AS std_milk,
    STD(p_fdays) AS std_days,
    STD(p_males + p_females) AS std_births,
    COUNT(p_bdate) AS count_births,
    AVG(p_males + p_females) AS avg_births
FROM production 
JOIN herds ON production.p_herd_id = herds.h_id
WHERE 1=1
  AND herds.h_breed_id = %(breed)s
  AND p_year BETWEEN %(year_from)s AND %(year_to)s
  AND production.p_fdays >= %(min_days)s
GROUP BY p_lact
ORDER BY p_lact;
"""
