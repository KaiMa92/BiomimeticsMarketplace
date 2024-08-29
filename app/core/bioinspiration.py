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
from .utils import create_results, string_to_json
from app.services.llm import assisted_chat

def bioinspire(query, model, client):
    if query == 'test': 
        return [{'title': 'Podargidae', 'description': 'The family Podargidae, which includes frogmouth birds, is known for their specialized wing structures that are optimized for silent and efficient flight. Their feathers have a lightweight and composite structure that reduces wing loading and optimizes lift-to-drag ratio. This structural optimization is crucial for a biomimetic aerial payload delivery system that needs to be light and efficient.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/9/90/Tawny_Frogmouth_%28Coverdale%29.jpg'}, {'title': 'Danaus plexippus', 'description': 'The Monarch butterfly (Danaus plexippus) showcases an exoskeleton with lightweight chitinous structures that provide strength without heavy mass. Their wings allow for highly efficient lift with low drag, crucial for long migratory flights. These traits can inspire lightweight composite materials for structural optimization in aerial delivery systems.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/e/e4/Danaus_plexippus_MHNT.jpg'}, {'title': 'Apidae', 'description': 'The honeybee (Apis mellifera) has an exoskeleton that provides a strong yet lightweight structure, crucial for tasks such as foraging and carrying pollen loads over long distances. Honeybee wings are highly optimized for efficient flight, with a favorable lift-to-drag ratio. Their flutter flight mechanics and exoskeleton composition can inspire design principles for lightweight, efficient payload delivery systems.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/f/f5/Apis_mellifera_carnica_worker_hive_entrance_2.jpg'}, {'title': 'Culicidae', 'description': 'Mosquitoes, particularly those in the family Culicidae, possess lightweight exoskeletons and wings that allow for efficient lift with minimal drag. Despite their small size, they can carry blood meals many times their body weight. The biomechanics of their wing loading and lift-to-drag optimization can inform the design of aerial payload delivery systems focusing on structural and weight efficiency.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/4/48/Aedes_aegypti_biting_human.jpg'}]
    else:
        keywords = assisted_chat(query, "CoreKeywordFinder1", model, client)
        bio_synonyms = assisted_chat(keywords, "Synonymfinder2", model, client)
        species = assisted_chat(bio_synonyms, "SpeciestoJASON4", model, client)
        sp_js = string_to_json(species)
        return create_results(sp_js)


