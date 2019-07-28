with abstract as (
    select id,
           string_agg(paragraph_text) as abstract_text
    from gcp_cset_clarivate.wos_abstract_paragraphs
    group by 1
),
kw as (
    select id,
           array_agg(keyword) as keywords
 from gcp_cset_clarivate.cset_wos_id_doi_keyword_table
 group by 1
)
select ai.id,
       title.title,
       kw.keywords,
       abstract.abstract_text
from gcp_cset_clarivate.cset_wos_basic_ai_id_list_en as ai
         inner join abstract
                    on ai.id = abstract.id
         inner join kw
                    on ai.id = kw.id
         inner join gcp_cset_clarivate.wos_titles as title
                    on ai.id = title.id
where title.title_type = 'item'
limit 1000;
