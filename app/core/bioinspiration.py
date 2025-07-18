# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

#categorize --> off-topic, Biology push, Technology pull

from app.core.expertfinder import filter_by_keyword, author_ranking, get_citations, summarize_nodes, explain_all_nodes
from .utils import agent_text
from llama_index.core.llms import ChatMessage
import pandas as pd

def format_multiline(text):
    formatted_data = text.replace('\n', '<br>')
    return formatted_data

def biomimetics_marketplace(query, llm, eng_sim, bio_sim): 

    location_filter = 'Frankfurt'
    top = 5


    print('categorize')
    #Categorize querys
    yield {'type': 'progress', 'message': 'Categorizing user query...'}
    categories = llm.chat([ChatMessage(role="user", content=query),ChatMessage(role='assistant', content = agent_text('agents/categorize.txt'))]).message.blocks[0].text

    if "Engineering" in categories: 
        summary_agent = agent_text('agents/bio_expert_summarize.txt')
        explain_agent = agent_text('agents/bio_documents_explain.txt')
        enrich_agent = agent_text('agents/enrich_eng_query.txt')
        search_expert_text = 'Search experts for analogous biosystems...'
        sim = bio_sim

    elif "Biology" in categories:
        summary_agent = agent_text('agents/bio_expert_summarize.txt')
        explain_agent = agent_text('agents/bio_documents_explain.txt')
        enrich_agent = agent_text('agents/enrich_eng_query.txt')
        search_expert_text = 'Search for skilled engineers...'
        sim = eng_sim
    
    else: 
        print('Should not land here')
        pass #error message necessary
    
    #Enrich engineering query
    yield {'type': 'progress', 'message': 'Enrich query...'}
    query = llm.chat([ChatMessage(role="user", content=query),ChatMessage(role='assistant', content = enrich_agent)]).message.blocks[0].text
    
    #Search experts
    yield {'type': 'progress', 'message': search_expert_text}
    retrieve_df = sim.retrieve(query)
    yield {'type': 'progress', 'message': 'Filter experts by location...'}
    filtered_df = filter_by_keyword(retrieve_df, location_filter)
    yield {'type': 'progress', 'message': 'Rank authors...'}
    ranked_authors_df = author_ranking(filtered_df)    
    df_top = ranked_authors_df.head(top)
    yield {'type': 'progress', 'message': 'Make IEEE references for sources...'}
    df_top['sources'] = df_top.apply(get_citations, args=(retrieve_df,), axis=1)
    unique_ids = sorted(set(id for sublist in df_top["nodes"] for id in sublist))
    id_mapping_df = pd.DataFrame({"node_id": unique_ids, "reference": range(1, len(unique_ids) + 1)})

    yield {'type': 'progress', 'message': 'Read abstracts...'}
    explanations = []
    # iterate through the values in the "nodes" column
    total_number_abstracts = sum(len(node_id_lst) for node_id_lst in df_top["nodes"])
    number_abstract = 0
    for node_id_lst in df_top["nodes"]:
        explanation_lst = []
        for node_id in node_id_lst: 
            number_abstract += 1
            paper_title = retrieve_df.loc[node_id]['Title']
            yield {'type': 'progress', 'message': 'Read abstract ' + str(number_abstract) + '/' + str(total_number_abstracts)+': "' + paper_title + '"...'}
            reference = id_mapping_df.loc[id_mapping_df['node_id']== node_id, 'reference'].values[0]
            query = 'Query: ' + query + 'System prompt:'
            explanation = sim.ask_node(node_id, query, agent_text) + ' ['+ str(reference) + ']'
            explanation_lst.append(explanation)
        explanations.append(explanation_lst)
    # assign the list back as the new column
    df_top["explanation"] = explanations

    df_top["explanation"] = df_top["nodes"].apply(lambda node_id_lst: explain_all_nodes(sim, node_id_lst, query, explain_agent, id_mapping_df))
    yield {'type': 'progress', 'message': 'Summarize author expertise...'}


    summaries = []

    for _, row in df_top.iterrows():
        yield {'type': 'progress', 'message': 'Summarize work of ' + row['author_name'] + '...'}
        summary = summarize_nodes(
            sim,
            query,
            summary_agent,
            row["explanation"],
            row["author_name"]
        )
        summaries.append(summary)
    df_top["summary"] = summaries

    df_top['affiliations'] = df_top['affiliations'].str[0]
    yield {'type': 'progress', 'message': 'Transform output...'}
    
    records = (
        df_top
        .sort_values("ranking")
        .loc[:, ["author_name", "summary", "affiliations", "sources"]]
        .to_dict(orient="records")
    )
    
    dct = {'Query': query, 
        'Location': location_filter, 
        'Authors': records}
    print(dct)
    yield {'type': 'results', 'data': dct}


def biomimetics_marketplace_dummy(query, llm, eng_sim, bio_sim):
    dct = {'Query': 'How can a plane fly more efficient?',
     'Location': 'Frankfurt',
     'Authors': [{'author_name': 'Mayr, Gerald',
       'summary': ' To make a plane fly more efficiently, we can look to the evolution of birds for inspiration. Here are some insights from the provided document snippets:\n\n1. **Muscle and Skeletal Structure**: The evolution of the supracoracoideus muscle and sternal keel in birds contributed to more efficient flight. Planes can be designed with analogous features, such as optimized structural supports and efficient power systems. [3]\n\n2. **Wing Design**: The discovery of a giant bony-toothed bird (Pelagornithidae) with a record-breaking wingspan provides insights into efficient wing design. Planes can adopt similar wing configurations for improved aerodynamics. [4]\n\n3. **Lightweight Structures**: The presence of lateral openings and pleurocoels in the thoracic vertebrae of birds enhances structural resistance while reducing weight. Planes can incorporate lightweight materials and designs inspired by these structures. [33]\n\n4. **Unique Body Plans**: New bird species from the Middle Eocene, like Eurofluvioviridavis robustipes, show unique body plans that may have contributed to efficient flight. Studying these can inspire innovative plane designs. [15]\n\n5. **Specialized Foraging Behavior**: The specialized foraging behavior or prey type of ?Palaeoplancus dammanni suggests unique adaptations for efficient flight. Planes can be designed with specialized features for different missions. [10]\n\nBy learning from the evolution and adaptations of birds, we can develop more efficient plane designs.',
       'affiliations': 'Ornithological Section, Senckenberg Research Institute and Natural History Museum Frankfurt, Senckenberganlage 25, Frankfurt am Main, 60325, Germany',
       'sources': ['[1] Mayr G., “Pectoral girdle morphology of Mesozoic birds and the evolution of the avian supracoracoideus muscle,” <i>Journal of Ornithology</i>, vol. 158, no. 3, pp. 859-867, 2017. DOI: <a href="https://doi.org/10.1007/s10336-017-1451-x">10.1007/s10336-017-1451-x</a>.',
        '[2] Mayr G.; Perner T., “A new species of diurnal birds of prey from the late eocene of wyoming (Usa) – one of the earliest new world records of the accipitridae (hawks, eagles, and allies),” <i>Neues Jahrbuch fur Geologie und Palaontologie - Abhandlungen</i>, vol. 297, no. 2, pp. 205-215, 2020. DOI: <a href="https://doi.org/10.1127/njgpa/2020/0921">10.1127/njgpa/2020/0921</a>.',
        '[3] Mayr G.; Rubilar-Rogers D., “Osteology of a new giant bony-toothed bird from the Miocene of Chile, with a revision of the taxonomy of Neogene Pelagornithidae,” <i>Journal of Vertebrate Paleontology</i>, vol. 30, no. 5, pp. 1313-1330, 2010. DOI: <a href="https://doi.org/10.1080/02724634.2010.501465">10.1080/02724634.2010.501465</a>.',
        '[4] Mayr G., “On the occurrence of lateral openings and fossae (pleurocoels) in the thoracic vertebrae of neornithine birds and their functional significance,” <i>Vertebrate Zoology</i>, vol. 71, no. nan, pp. 453-463, 2021. DOI: <a href="https://doi.org/10.3897/VZ.71.E71268">10.3897/VZ.71.E71268</a>.',
        '[5] Mayr G.; Hazevoet C.J.; Dantas P.; Cachão M., “A sternum of a very large bony-toothed bird (Pelagornithidae) from the Miocene of Portugal,” <i>Journal of Vertebrate Paleontology</i>, vol. 28, no. 3, pp. 762-769, 2008. DOI: <a href="https://doi.org/10.1671/0272-4634(2008)28[762:ASOAVL]2.0.CO;2">10.1671/0272-4634(2008)28[762:ASOAVL]2.0.CO;2</a>.',
        '[6] Mayr G., “A Fluvioviridavis-like bird from the Middle Eocene of Messel, Germany,” <i>Canadian Journal of Earth Sciences</i>, vol. 42, no. 11, pp. 2021-2037, 2005. DOI: <a href="https://doi.org/10.1139/e05-060">10.1139/e05-060</a>.',
        '[7] Mayr G., “Skeletal morphology of the middle eocene swift Scaniacypselus and the evolutionary history of true swifts (Apodidae); [Skelettmorphologie des mitteleozänen Seglers Scaniacypselus und die Evolutionsgeschichte echter Segler (Apodidae)],” <i>Journal of Ornithology</i>, vol. 156, no. 2, pp. 441-450, 2014. DOI: <a href="https://doi.org/10.1007/s10336-014-1142-9">10.1007/s10336-014-1142-9</a>.']},
      {'author_name': 'Schleuning, Matthias',
       'summary': " It seems there might have been a misunderstanding in your query. The document snippets provided are related to ecological studies, particularly focusing on birds, plants, and their interactions. They do not contain information about how a plane can fly more efficiently.\n\nTo address your query about making a plane fly more efficiently, here are some general strategies:\n\n1. **Weight Reduction**: Reducing the weight of the aircraft can significantly improve fuel efficiency. This can be achieved by using lighter materials, optimizing the design, and reducing the load.\n\n2. **Aerodynamics**: Improving the aerodynamics of the plane can reduce drag and thus improve efficiency. This includes designing more efficient wing shapes, reducing the aircraft's surface roughness, and optimizing the overall shape of the plane.\n\n3. **Engine Efficiency**: Advances in engine technology can lead to more efficient fuel consumption. This includes using more efficient combustion processes, reducing engine weight, and optimizing engine performance.\n\n4. **Flight Path Optimization**: Optimizing the flight path can also improve efficiency. This includes flying at the most efficient altitude and speed, avoiding turbulence, and taking advantage of favorable winds.\n\n5. **Hybrid and Electric Propulsion**: The development of hybrid and electric propulsion systems can reduce or eliminate the need for fossil fuels, making the plane more environmentally friendly and potentially more efficient.\n\n6. **Maintenance**: Regular maintenance can ensure that all systems are working optimally, which can improve overall efficiency.\n\nIf you have specific aspects of plane efficiency you're interested in, please let me know!",
       'affiliations': 'Senckenberg Biodiversity and Climate Research Centre (SBiK-F), Senckenberganlage 25, Frankfurt am Main, 60325, Germany',
       'sources': ['[1] Martins L.P.; Stouffer D.B.; Blendinger P.G.; Böhning-Gaese K.; Costa J.M.; Dehling D.M.; Donatti C.I.; Emer C.; Galetti M.; Heleno R.; Menezes Í.; Morante-Filho J.C.; Muñoz M.C.; Neuschulz E.L.; Pizo M.A.; Quitián M.; Ruggera R.A.; Saavedra F.; Santillán V.; Schleuning M.; da Silva L.P.; Ribeiro da Silva F.; Tobias J.A.; Traveset A.; Vollstädt M.G.R.; Tylianakis J.M., “Birds optimize fruit size consumed near their geographic range limits,” <i>Science (New York, N.Y.)</i>, vol. 385, no. 6706, pp. 331-336, 2024. DOI: <a href="https://doi.org/10.1126/science.adj1856">10.1126/science.adj1856</a>.',
        '[2] Nowak L.; Schleuning M.; Bender I.M.A.; Böhning-Gaese K.; Dehling D.M.; Fritz S.A.; Kissling W.D.; Mueller T.; Neuschulz E.L.; Pigot A.L.; Sorensen M.C.; Donoso I., “Avian seed dispersal may be insufficient for plants to track future temperature change on tropical mountains,” <i>Global Ecology and Biogeography</i>, vol. 31, no. 5, pp. 848-860, 2022. DOI: <a href="https://doi.org/10.1111/geb.13456">10.1111/geb.13456</a>.',
        '[3] Junker R.R.; Albrecht J.; Becker M.; Keuth R.; Farwig N.; Schleuning M., “Towards an animal economics spectrum for ecosystem research,” <i>Functional Ecology</i>, vol. 37, no. 1, pp. 57-72, 2023. DOI: <a href="https://doi.org/10.1111/1365-2435.14051">10.1111/1365-2435.14051</a>.',
        '[4] Thiel S.; Willems F.; Farwig N.; Rehling F.; Schabo D.G.; Schleuning M.; Shahuano\xa0Tello N.; Töpfer T.; Tschapka M.; Heymann E.W.; Heer K., “Vertically stratified frugivore community composition and interaction frequency in a liana fruiting across forest strata,” <i>Biotropica</i>, vol. 55, no. 3, pp. 650-664, 2023. DOI: <a href="https://doi.org/10.1111/btp.13216">10.1111/btp.13216</a>.',
        '[5] Saavedra F.; Hensen I.; Schleuning M., “Deforested habitats lack seeds of late-successional and large-seeded plant species in tropical montane forests,” <i>Applied Vegetation Science</i>, vol. 18, no. 4, pp. 603-612, 2015. DOI: <a href="https://doi.org/10.1111/avsc.12184">10.1111/avsc.12184</a>.',
        '[6] Muñoz M.C.; Schaefer H.M.; Böhning-Gaese K.; Schleuning M., “Positive relationship between fruit removal by animals and seedling recruitment in a tropical forest,” <i>Basic and Applied Ecology</i>, vol. 20, no. nan, pp. 31-39, 2017. DOI: <a href="https://doi.org/10.1016/j.baae.2017.03.001">10.1016/j.baae.2017.03.001</a>.',
        '[7] Acosta-Rojas D.C.; Barczyk M.K.; Espinosa C.I.; Tinoco B.A.; Neuschulz E.L.; Schleuning M., “Systematic reduction in seed rain of large-seeded and endozoochorous species in pastures compared to forests along a tropical elevational gradient,” <i>Applied Vegetation Science</i>, vol. 27, no. 2, pp. nan-nan, 2024. DOI: <a href="https://doi.org/10.1111/avsc.12780">10.1111/avsc.12780</a>.',
        '[8] Vogeler A.-V.B.; Otte I.; Ferger S.; Helbig-Bonitz M.; Hemp A.; Nauss T.; Böhning-Gaese K.; Schleuning M.; Tschapka M.; Albrecht J., “Associations of bird and bat species richness with temperature and remote sensing-based vegetation structure on a tropical mountain,” <i>Biotropica</i>, vol. 54, no. 1, pp. 135-145, 2022. DOI: <a href="https://doi.org/10.1111/btp.13037">10.1111/btp.13037</a>.']},
      {'author_name': 'Böhning-Gaese, Katrin',
       'summary': " The document snippets provided do not directly address the query about how a plane can fly more efficiently. However, one snippet discusses morphological adaptations of migratory birds, specifically mentioning longer, more pointed wings and shorter tails, which are features that can also be applied to aircraft design to improve flight efficiency. These adaptations can reduce drag and enhance lift, making flight more efficient.\n\nTo make a plane fly more efficiently, several strategies can be considered:\n\n1. **Aerodynamic Design**: Streamline the plane's body and wings to reduce drag. Longer, more pointed wings, similar to those of migratory birds, can improve lift and reduce induced drag.\n\n2. **Weight Reduction**: Lighter aircraft require less fuel to fly, so reducing the weight of the plane through the use of lighter materials or efficient design can improve efficiency.\n\n3. **Engine Efficiency**: Improve the efficiency of the plane's engines. This can involve using more fuel-efficient engines, optimizing engine performance, or exploring alternative propulsion systems.\n\n4. **Flight Path Optimization**: Plan flight paths to take advantage of favorable winds and avoid turbulence. This can reduce the amount of fuel required to reach the destination.\n\n5. **Advanced Technologies**: Incorporate advanced technologies such as hybrid-electric or fully electric propulsion systems, which can be more efficient than traditional jet engines.\n\n6. **Maintenance**: Regular maintenance ensures that all components of the plane are functioning optimally, which can improve overall efficiency.\n\nThese strategies can help make a plane fly more efficiently, reducing fuel consumption and environmental impact.",
       'affiliations': 'Senckenberg Biodiversity and Climate Research Centre (SBiK-F), Senckenberganlage 25, Frankfurt am Main, 60325, Germany, Institute for Ecology, Evolution and Diversity, Goethe University Frankfurt ,Max-von-Laue-Straße 13, Frankfurt am Main, 60439, Germany',
       'sources': ['[1] Martins L.P.; Stouffer D.B.; Blendinger P.G.; Böhning-Gaese K.; Costa J.M.; Dehling D.M.; Donatti C.I.; Emer C.; Galetti M.; Heleno R.; Menezes Í.; Morante-Filho J.C.; Muñoz M.C.; Neuschulz E.L.; Pizo M.A.; Quitián M.; Ruggera R.A.; Saavedra F.; Santillán V.; Schleuning M.; da Silva L.P.; Ribeiro da Silva F.; Tobias J.A.; Traveset A.; Vollstädt M.G.R.; Tylianakis J.M., “Birds optimize fruit size consumed near their geographic range limits,” <i>Science (New York, N.Y.)</i>, vol. 385, no. 6706, pp. 331-336, 2024. DOI: <a href="https://doi.org/10.1126/science.adj1856">10.1126/science.adj1856</a>.',
        '[2] Phillips A.G.; Töpfer T.; Böhning-Gaese K.; Fritz S.A., “Evidence for distinct evolutionary optima in the morphology of migratory and resident birds,” <i>Journal of Avian Biology</i>, vol. 49, no. 10, pp. nan-nan, 2018. DOI: <a href="https://doi.org/10.1111/jav.01807">10.1111/jav.01807</a>.',
        '[3] Tucker M.A.; Alexandrou O.; Bierregaard R.O., Jr.; Bildstein K.L.; Böhning-Gaese K.; Bracis C.; Brzorad J.N.; Buechley E.R.; Cabot D.; Calabrese J.M.; Carrapato C.; Chiaradia A.; Davenport L.C.; Davidson S.C.; Desholm M.; DeSorbo C.R.; Domenech R.; Enggist P.; Fagan W.F.; Farwig N.; Fiedler W.; Fleming C.H.; Franke A.; Fryxell J.M.; García-Ripollés C.; Grémillet D.; Griffin L.R.; Harel R.; Kane A.; Kays R.; Kleyheeg E.; Lacy A.E.; LaPoint S.; Limiñana R.; López-López P.; Maccarone A.D.; Mellone U.; Mojica E.K.; Nathan R.; Newman S.H.; Noonan M.J.; Oppel S.; Prostor M.; Rees E.C.; Ropert-Coudert Y.; Rösner S.; Sapir N.; Schabo D.; Schmidt M.; Schulz H.; Shariati M.; Shreading A.; Paulo Silva J.; Skov H.; Spiegel O.; Takekawa J.Y.; Teitelbaum C.S.; van Toor M.L.; Urios V.; Vidal-Mateo J.; Wang Q.; Watts B.D.; Wikelski M.; Wolter K.; Žydelis R.; Mueller T., “Large birds travel farther in homogeneous environments,” <i>Global Ecology and Biogeography</i>, vol. 28, no. 5, pp. 576-587, 2019. DOI: <a href="https://doi.org/10.1111/geb.12875">10.1111/geb.12875</a>.',
        '[4] Nowak L.; Schleuning M.; Bender I.M.A.; Böhning-Gaese K.; Dehling D.M.; Fritz S.A.; Kissling W.D.; Mueller T.; Neuschulz E.L.; Pigot A.L.; Sorensen M.C.; Donoso I., “Avian seed dispersal may be insufficient for plants to track future temperature change on tropical mountains,” <i>Global Ecology and Biogeography</i>, vol. 31, no. 5, pp. 848-860, 2022. DOI: <a href="https://doi.org/10.1111/geb.13456">10.1111/geb.13456</a>.',
        '[5] Mallon J.M.; Tucker M.A.; Beard A.; Bierregaard R.O., Jr.; Bildstein K.L.; Böhning-Gaese K.; Brzorad J.N.; Buechley E.R.; Bustamante J.; Carrapato C.; Castillo-Guerrero J.A.; Clingham E.; Desholm M.; DeSorbo C.R.; Domenech R.; Douglas H.; Duriez O.; Enggist P.; Farwig N.; Fiedler W.; Gagliardo A.; García-Ripollés C.; Gil Gallús J.A.; Gilmour M.E.; Harel R.; Harrison A.-L.; Henry L.; Katzner T.E.; Kays R.; Kleyheeg E.; Limiñana R.; López-López P.; Lucia G.; Maccarone A.; Mallia E.; Mellone U.; Mojica E.K.; Nathan R.; Newman S.H.; Oppel S.; Orchan Y.; Prosser D.J.; Riley H.; Rösner S.; Schabo D.G.; Schulz H.; Shaffer S.; Shreading A.; Silva J.P.; Sim J.; Skov H.; Spiegel O.; Stuber M.J.; Takekawa J.Y.; Urios V.; Vidal-Mateo J.; Warner K.; Watts B.D.; Weber N.; Weber S.; Wikelski M.; Žydelis R.; Mueller T.; Fagan W.F., “Diurnal timing of nonmigratory movement by birds: the importance of foraging spatial scales,” <i>Journal of Avian Biology</i>, vol. 51, no. 12, pp. nan-nan, 2020. DOI: <a href="https://doi.org/10.1111/jav.02612">10.1111/jav.02612</a>.',
        '[6] Muñoz M.C.; Schaefer H.M.; Böhning-Gaese K.; Schleuning M., “Positive relationship between fruit removal by animals and seedling recruitment in a tropical forest,” <i>Basic and Applied Ecology</i>, vol. 20, no. nan, pp. 31-39, 2017. DOI: <a href="https://doi.org/10.1016/j.baae.2017.03.001">10.1016/j.baae.2017.03.001</a>.',
        '[7] Mueller T.; Lenz J.; Caprano T.; Fiedler W.; Böhning-Gaese K., “Large frugivorous birds facilitate functional connectivity of fragmented landscapes,” <i>Journal of Applied Ecology</i>, vol. 51, no. 3, pp. 684-692, 2014. DOI: <a href="https://doi.org/10.1111/1365-2664.12247">10.1111/1365-2664.12247</a>.',
        '[8] Vogeler A.-V.B.; Otte I.; Ferger S.; Helbig-Bonitz M.; Hemp A.; Nauss T.; Böhning-Gaese K.; Schleuning M.; Tschapka M.; Albrecht J., “Associations of bird and bat species richness with temperature and remote sensing-based vegetation structure on a tropical mountain,” <i>Biotropica</i>, vol. 54, no. 1, pp. 135-145, 2022. DOI: <a href="https://doi.org/10.1111/btp.13037">10.1111/btp.13037</a>.']},
      {'author_name': 'Haase, Peter',
       'summary': ' It seems that the provided document snippets do not directly address the query about how a plane can fly more efficiently. The snippets primarily discuss various studies related to insects, plants, and environmental conditions, but they do not contain information relevant to aircraft efficiency. To better assist with the query, I would need access to documents or information specifically related to aviation and aircraft efficiency.',
       'affiliations': 'Department of River Ecology and Conservation, Senckenberg Research Institute and Natural History Museum Frankfurt, Gelnhausen, Germany, Faculty of Biology, University of Duisburg-Essen, Essen, Germany',
       'sources': ['[1] Jourdan J.; Baranov V.; Wagner R.; Plath M.; Haase P., “Elevated temperatures translate into reduced dispersal abilities in a natural population of an aquatic insect,” <i>Journal of Animal Ecology</i>, vol. 88, no. 10, pp. 1498-1509, 2019. DOI: <a href="https://doi.org/10.1111/1365-2656.13054">10.1111/1365-2656.13054</a>.',
        '[2] Hoffmann L.; Palt M.; Mignien L.; Uhler J.; Haase P.; Müller J.; Stoll S., “Effects of species traits on the catchability of butterflies with different types of Malaise traps and implications for total catch biomass,” <i>Journal of Insect Conservation</i>, vol. 29, no. 1, pp. nan-nan, 2025. DOI: <a href="https://doi.org/10.1007/s10841-024-00645-5">10.1007/s10841-024-00645-5</a>.',
        '[3] Ahmed D.A.; Beidas A.; Petrovskii S.V.; Bailey J.D.; Bonsall M.B.; Hood A.S.C.; Byers J.A.; Hudgins E.J.; Russell J.C.; Růžičková J.; Bodey T.W.; Renault D.; Bonnaud E.; Haubrock P.J.; Soto I.; Haase P., “Simulating capture efficiency of pitfall traps based on sampling strategy and the movement of ground-dwelling arthropods,” <i>Methods in Ecology and Evolution</i>, vol. 14, no. 11, pp. 2827-2843, 2023. DOI: <a href="https://doi.org/10.1111/2041-210X.14174">10.1111/2041-210X.14174</a>.',
        '[4] Kappes H.; Tackenberg O.; Haase P., “Differences in dispersal- and colonization-related traits between taxa from the freshwater and the terrestrial realm,” <i>Aquatic Ecology</i>, vol. 48, no. 1, pp. 73-83, 2014. DOI: <a href="https://doi.org/10.1007/s10452-013-9467-7">10.1007/s10452-013-9467-7</a>.',
        '[5] Engelhardt C.H.M.; Haase P.; Pauls S.U., “From the Western Alps across Central Europe: Postglacial recolonisation of the tufa stream specialist Rhyacophila pubescens (Insecta, Trichoptera),” <i>Frontiers in Zoology</i>, vol. 8, no. nan, pp. nan-nan, 2011. DOI: <a href="https://doi.org/10.1186/1742-9994-8-10">10.1186/1742-9994-8-10</a>.']},
      {'author_name': 'Mueller, Thomas',
       'summary': ' Based on the provided document snippets, here are some ways planes could potentially fly more efficiently inspired by bird migration studies:\n\n1. **Social Learning and Experience**: Planes could be equipped with AI or machine learning systems that learn from experienced pilots or other planes to optimize routes and improve flight efficiency, similar to how migrating whooping cranes improve their paths through social learning. [11]\n\n2. **Early-life Experience**: Just as early-life experiences influence the flight proficiency of Egyptian vultures, planes could be "trained" or calibrated early on to optimize their performance. This could involve testing and adjusting planes under various conditions during initial flights. [31]\n\n3. **Adaptive Timing and Flight Modes**: Planes could adapt their flight modes and timing based on the situation, similar to how birds adjust their daily activity patterns based on foraging strategies. For instance, planes could switch between different flight modes to optimize fuel efficiency depending on wind conditions or other factors. [16]\n\n4. **Optimized Routes for Changing Conditions**: Planes could use real-time data to adjust their routes to account for changing conditions, such as temperature shifts or weather patterns, similar to how bird-dispersed plant species migrate to track temperature shifts. [13]\n\n5. **Phase-specific Optimization**: Planes could optimize their performance for different phases of flight (takeoff, cruising, landing) based on data analysis, similar to how Egyptian vultures have different survival rates and presumably different strategies for different phases of their migratory cycle. [23]',
       'affiliations': 'Department of Biology, University of Maryland, College Park, MD 20742, United States, Biodiversity and Climate Research Centre (BiK-F), Senckenberg Gesellschaft für Naturforschung, Goethe Universität Frankfurt, 60325 Frankfurt (Main), Senckenberganlage 25, Germany, Smithsonian Conservation Biology Institute, National Zoological Park, Front Royal, VA 22630, 1500 Remount Road, United States',
       'sources': ['[1] Mueller T.; O\'Hara R.B.; Converse S.J.; Urbanek R.P.; Fagan W.F., “Social learning of migratory performance,” <i>Science</i>, vol. 341, no. 6149, pp. 999-1002, 2013. DOI: <a href="https://doi.org/10.1126/science.1237139">10.1126/science.1237139</a>.',
        '[2] Efrat R.; Hatzofe O.; Mueller T.; Sapir N.; Berger-Tal O., “Early and accumulated experience shape migration and flight in Egyptian vultures,” <i>Current Biology</i>, vol. 33, no. 24, pp. 5526-5532.e4, 2023. DOI: <a href="https://doi.org/10.1016/j.cub.2023.11.012">10.1016/j.cub.2023.11.012</a>.',
        '[3] Nowak L.; Schleuning M.; Bender I.M.A.; Böhning-Gaese K.; Dehling D.M.; Fritz S.A.; Kissling W.D.; Mueller T.; Neuschulz E.L.; Pigot A.L.; Sorensen M.C.; Donoso I., “Avian seed dispersal may be insufficient for plants to track future temperature change on tropical mountains,” <i>Global Ecology and Biogeography</i>, vol. 31, no. 5, pp. 848-860, 2022. DOI: <a href="https://doi.org/10.1111/geb.13456">10.1111/geb.13456</a>.',
        '[4] Mallon J.M.; Tucker M.A.; Beard A.; Bierregaard R.O., Jr.; Bildstein K.L.; Böhning-Gaese K.; Brzorad J.N.; Buechley E.R.; Bustamante J.; Carrapato C.; Castillo-Guerrero J.A.; Clingham E.; Desholm M.; DeSorbo C.R.; Domenech R.; Douglas H.; Duriez O.; Enggist P.; Farwig N.; Fiedler W.; Gagliardo A.; García-Ripollés C.; Gil Gallús J.A.; Gilmour M.E.; Harel R.; Harrison A.-L.; Henry L.; Katzner T.E.; Kays R.; Kleyheeg E.; Limiñana R.; López-López P.; Lucia G.; Maccarone A.; Mallia E.; Mellone U.; Mojica E.K.; Nathan R.; Newman S.H.; Oppel S.; Orchan Y.; Prosser D.J.; Riley H.; Rösner S.; Schabo D.G.; Schulz H.; Shaffer S.; Shreading A.; Silva J.P.; Sim J.; Skov H.; Spiegel O.; Stuber M.J.; Takekawa J.Y.; Urios V.; Vidal-Mateo J.; Warner K.; Watts B.D.; Weber N.; Weber S.; Wikelski M.; Žydelis R.; Mueller T.; Fagan W.F., “Diurnal timing of nonmigratory movement by birds: the importance of foraging spatial scales,” <i>Journal of Avian Biology</i>, vol. 51, no. 12, pp. nan-nan, 2020. DOI: <a href="https://doi.org/10.1111/jav.02612">10.1111/jav.02612</a>.',
        '[5] Buechley E.R.; Oppel S.; Efrat R.; Phipps W.L.; Carbonell Alanís I.; Álvarez E.; Andreotti A.; Arkumarev V.; Berger-Tal O.; Bermejo Bermejo A.; Bounas A.; Ceccolini G.; Cenerini A.; Dobrev V.; Duriez O.; García J.; García-Ripollés C.; Galán M.; Gil A.; Giraud L.; Hatzofe O.; Iglesias-Lebrija J.J.; Karyakin I.; Kobierzycki E.; Kret E.; Loercher F.; López-López P.; Miller Y.; Mueller T.; Nikolov S.C.; de la Puente J.; Sapir N.; Saravia V.; Şekercioğlu Ç.H.; Sillett T.S.; Tavares J.; Urios V.; Marra P.P., “Differential survival throughout the full annual cycle of a migratory bird presents a life-history trade-off,” <i>Journal of Animal Ecology</i>, vol. 90, no. 5, pp. 1228-1238, 2021. DOI: <a href="https://doi.org/10.1111/1365-2656.13449">10.1111/1365-2656.13449</a>.']}]}

    yield {'type': 'results', 'data': dct}