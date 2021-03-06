###############################################################################
# Author: Wasi Ahmad
# Project: Match Tensor: a Deep Relevance Model for Search
# Date Created: 7/28/2017
#
# File Description: This script contains code related to the neural network layers.
###############################################################################

import torch, helper
import numpy as np
import torch.nn as nn
from torch.nn import init
from collections import OrderedDict


class EmbeddingLayer(nn.Module):
    """Embedding class which includes only an embedding layer."""

    def __init__(self, input_size, config):
        """"Constructor of the class"""
        super(EmbeddingLayer, self).__init__()
        if config.emtraining:
            self.embedding = nn.Sequential(OrderedDict([
                ('embedding', nn.Embedding(input_size, config.emsize)),
                ('dropout', nn.Dropout(config.dropout))
            ]))
        else:
            self.embedding = nn.Embedding(input_size, config.emsize)
            self.embedding.weight.requires_grad = False

    def forward(self, input_variable):
        """"Defines the forward computation of the embedding layer."""
        return self.embedding(input_variable)

    def init_embedding_weights(self, dictionary, embeddings_index, embedding_dim):
        """Initialize weight parameters for the embedding layer."""
        pretrained_weight = np.empty([len(dictionary), embedding_dim], dtype=float)
        for i in range(len(dictionary)):
            if dictionary.idx2word[i] in embeddings_index:
                pretrained_weight[i] = embeddings_index[dictionary.idx2word[i]]
            else:
                pretrained_weight[i] = helper.initialize_out_of_vocab_words(embedding_dim)
        # pretrained_weight is a numpy matrix of shape (num_embeddings, embedding_dim)
        if isinstance(self.embedding, nn.Sequential):
            self.embedding[0].weight.data.copy_(torch.from_numpy(pretrained_weight))
        else:
            self.embedding.weight.data.copy_(torch.from_numpy(pretrained_weight))


class GatingNetwork(nn.Module):
    """Term gating network"""

    def __init__(self, emsize):
        """"Constructor of the class"""
        super(GatingNetwork, self).__init__()
        self.weight = nn.Parameter(torch.Tensor(emsize))
        init.uniform(self.weight)

    def forward(self, term_embeddings):
        """"Defines the forward computation of the gating network layer."""
        dot_out = torch.sum(self.weight.expand(*term_embeddings.size()) * term_embeddings, 2).squeeze()
        return nn.functional.softmax(dot_out, 1)
