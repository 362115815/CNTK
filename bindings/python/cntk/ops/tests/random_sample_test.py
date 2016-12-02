# Copyright (c) Microsoft. All rights reserved.

# Licensed under the MIT license. See LICENSE.md file in the project root
# for full license information.
# ==============================================================================

"""
Unit tests random sampling related operations
"""

import numpy as np
import pytest
from .ops_test_utils import AA, precision
from  cntk import random_sample_inclusion_frequency, random_sample, times

TEST_CASES = [
    # drawing 1 sample
    (np.full((4), 42.),                                                               1,     True,   np.full((4), 1/4),                                    0.0001, False),

    # drawing 13 samples
    (np.full((4), 42.),                                                              13,     True,   np.full((4), 13/4),                                   0.0001, False),

    # drawing more samples than there are classes
    ([1.,2.,3.],                                                                     42,     True,   [42/(1+2+3), 2*42/(1+2+3), 3*42/(1+2+3)],             0.0001, False),

    # Use 300 weights where the first 200 hundred weights are high compared to the rest. Sample 200 without replacement. 
    (np.concatenate((np.full((100),100),np.full((100),10),np.full((100),0.1))),    200,      False,  np.concatenate((np.full((200),1),np.full((100),0))),  0.1,   False),
    
    # Having more classes than samples is not allowed when sampling without replacment. Check if exception is thrown.
    (np.full((4), 42.),                                                              50,     False,  np.full((4), 13/4),                                   0.0001, True), 

    # Number of requested samples must be positive
    ([1., 2., 3.],                                                                    0,     False,  np.full((4), 13/4),                                   0.0001, True), 

    # Negative sampling weigts are not allowed.
    ([1,-1.],                                                                         1,     True,   [0],                                                  0.0001, True), 
    ([1,-1.],                                                                         1,     False,  [0],                                                  0.0001, True), 
]

@pytest.mark.parametrize("weights, num_samples, allow_duplicates, expected, tolerance, raises_exception", TEST_CASES)
def test_random_sample_inclusion_frequency(weights, num_samples, allow_duplicates, expected, tolerance, raises_exception, device_id, precision):

    weights = AA(weights);

    if raises_exception:
        with pytest.raises(ValueError):
            result = random_sample_inclusion_frequency(weights, num_samples, allow_duplicates)
            result.eval()
    else:
        result = random_sample_inclusion_frequency(weights, num_samples, allow_duplicates)
        assert np.allclose(result.eval(), expected, atol=tolerance)

# BUGBUG add test for random_sample(...) too.

RANDOM_SAMPLE_TEST_CASES_WITH_REPLACEMENT = [
    ([1., 3., 5., 1.],  1000, 0.03, False),
    ([1., -1.],  100, 0.0, True),
]
@pytest.mark.parametrize("weights, num_samples,  tolerance, raises_exception", RANDOM_SAMPLE_TEST_CASES_WITH_REPLACEMENT)
def test_random_sample_with_replacement(weights, num_samples,  tolerance, raises_exception, device_id, precision):

    weights = AA(weights);
    expected_relative_frequency = weights / np.sum(weights)
    num_calls = 10;
    identity = np.identity(weights.size)
    allow_duplicates = True # sample with replacement

    if raises_exception:
        with pytest.raises(ValueError):
            result = random_sample(weights, num_samples, allow_duplicates)
            result.eval()
    else:
        observed_frequency = np.empty_like(weights)
        for i in range(0, num_calls):
            result = random_sample(weights, num_samples, allow_duplicates)
            denseResult = times(result, identity)
            observed_frequency += np.sum(denseResult.eval(), 0)
        observed_relative_frequency = observed_frequency / (num_calls * num_samples)
        assert np.allclose(observed_relative_frequency, expected_relative_frequency, atol=tolerance)

        

RANDOM_SAMPLE_TEST_CASES_WITHOUT_REPLACEMENT = [
    ([1., 3, 50., 1., 0.], 4, (0.25, 0.25, 0.25, 0.25, 0), 0.03, False),
    ([1., -1.],  1, None,   0.0, True),
]
@pytest.mark.parametrize("weights, num_samples, expected_relative_frequency, tolerance, raises_exception", RANDOM_SAMPLE_TEST_CASES_WITHOUT_REPLACEMENT)
def test_random_sample_without_replacement(weights, num_samples, expected_relative_frequency, tolerance, raises_exception, device_id, precision):

    weights = AA(weights);
    num_calls = 1;
    identity = np.identity(weights.size)
    allow_duplicates = False # sample without replacement

    if raises_exception:
        with pytest.raises(ValueError):
            result = random_sample(weights, num_samples, allow_duplicates)
            result.eval()
    else:
        observed_frequency = np.zeros_like(weights)
        for i in range(0, num_calls):
            result = random_sample(weights, num_samples, allow_duplicates)
            denseResult = times(result, identity)
            observed_frequency += np.sum(denseResult.eval(), 0)
        observed_frequency /= (num_calls * num_samples)
        assert np.allclose(observed_frequency, expected_relative_frequency, atol=tolerance)

