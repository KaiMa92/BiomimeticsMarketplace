# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

import pytest
from unittest.mock import patch
from app.core.bioinspiration import bioinspire
from app.services.llm import assisted_chat
from app.core.utils import create_results, string_to_json

@pytest.fixture
def query():
    return "biological inspiration"

@pytest.fixture
def model():
    return "gpt-4"

@pytest.fixture
def mock_client():
    # Assuming your client is a complex object, you can mock it or create a dummy instance
    return "mocked_client"

# Mocking the dependencies
@patch('app.core.bioinspiration.assisted_chat')
@patch('app.core.bioinspiration.string_to_json')
@patch('app.core.bioinspiration.create_results')
def test_bioinspire(mock_create_results, mock_string_to_json, mock_assisted_chat, query, model, mock_client):
    # Set up the mock return values for the functions being called
    mock_assisted_chat.side_effect = [
        "keyword_results",  # First call returns keywords
        "bio_synonyms_results",  # Second call returns bio_synonyms
        "species_results"  # Third call returns species
    ]
    mock_string_to_json.return_value = [{'title': 'Podargidae', 'description': 'The family Podargidae, which includes frogmouth birds, is known for their specialized wing structures that are optimized for silent and efficient flight. Their feathers have a lightweight and composite structure that reduces wing loading and optimizes lift-to-drag ratio. This structural optimization is crucial for a biomimetic aerial payload delivery system that needs to be light and efficient.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/9/90/Tawny_Frogmouth_%28Coverdale%29.jpg'}, {'title': 'Danaus plexippus', 'description': 'The Monarch butterfly (Danaus plexippus) showcases an exoskeleton with lightweight chitinous structures that provide strength without heavy mass. Their wings allow for highly efficient lift with low drag, crucial for long migratory flights. These traits can inspire lightweight composite materials for structural optimization in aerial delivery systems.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/e/e4/Danaus_plexippus_MHNT.jpg'}, {'title': 'Apidae', 'description': 'The honeybee (Apis mellifera) has an exoskeleton that provides a strong yet lightweight structure, crucial for tasks such as foraging and carrying pollen loads over long distances. Honeybee wings are highly optimized for efficient flight, with a favorable lift-to-drag ratio. Their flutter flight mechanics and exoskeleton composition can inspire design principles for lightweight, efficient payload delivery systems.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/f/f5/Apis_mellifera_carnica_worker_hive_entrance_2.jpg'}, {'title': 'Culicidae', 'description': 'Mosquitoes, particularly those in the family Culicidae, possess lightweight exoskeletons and wings that allow for efficient lift with minimal drag. Despite their small size, they can carry blood meals many times their body weight. The biomechanics of their wing loading and lift-to-drag optimization can inform the design of aerial payload delivery systems focusing on structural and weight efficiency.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/4/48/Aedes_aegypti_biting_human.jpg'}]  # Mock the JSON conversion
    mock_create_results.return_value = "final_results"  # Mock the final result creation

    # Call the function you're testing
    result = bioinspire(query, model, mock_client)

    # Assertions to ensure the function behaves as expected
    assert result == "final_results"  # Ensure the final result is as expected

    # Verify that the assisted_chat function was called three times with expected arguments
    mock_assisted_chat.assert_any_call(query, "CoreKeywordFinder1", model, mock_client)
    mock_assisted_chat.assert_any_call("keyword_results", "Synonymfinder2", model, mock_client)
    mock_assisted_chat.assert_any_call("bio_synonyms_results", "SpeciestoJASON4", model, mock_client)

    # Verify that string_to_json and create_results were called with the right arguments
    mock_string_to_json.assert_called_once_with("species_results")
    mock_create_results.assert_called_once_with([{'title': 'Podargidae', 'description': 'The family Podargidae, which includes frogmouth birds, is known for their specialized wing structures that are optimized for silent and efficient flight. Their feathers have a lightweight and composite structure that reduces wing loading and optimizes lift-to-drag ratio. This structural optimization is crucial for a biomimetic aerial payload delivery system that needs to be light and efficient.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/9/90/Tawny_Frogmouth_%28Coverdale%29.jpg'}, {'title': 'Danaus plexippus', 'description': 'The Monarch butterfly (Danaus plexippus) showcases an exoskeleton with lightweight chitinous structures that provide strength without heavy mass. Their wings allow for highly efficient lift with low drag, crucial for long migratory flights. These traits can inspire lightweight composite materials for structural optimization in aerial delivery systems.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/e/e4/Danaus_plexippus_MHNT.jpg'}, {'title': 'Apidae', 'description': 'The honeybee (Apis mellifera) has an exoskeleton that provides a strong yet lightweight structure, crucial for tasks such as foraging and carrying pollen loads over long distances. Honeybee wings are highly optimized for efficient flight, with a favorable lift-to-drag ratio. Their flutter flight mechanics and exoskeleton composition can inspire design principles for lightweight, efficient payload delivery systems.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/f/f5/Apis_mellifera_carnica_worker_hive_entrance_2.jpg'}, {'title': 'Culicidae', 'description': 'Mosquitoes, particularly those in the family Culicidae, possess lightweight exoskeletons and wings that allow for efficient lift with minimal drag. Despite their small size, they can carry blood meals many times their body weight. The biomechanics of their wing loading and lift-to-drag optimization can inform the design of aerial payload delivery systems focusing on structural and weight efficiency.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/4/48/Aedes_aegypti_biting_human.jpg'}])
