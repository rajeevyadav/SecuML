## SecuML
## Copyright (C) 2016  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

import copy
import numpy as np
import pandas as pd
from sklearn import decomposition

from UnsupervisedProjection import UnsupervisedProjection

class Pca(UnsupervisedProjection):

    def __init__(self, experiment):
        UnsupervisedProjection.__init__(self, experiment)
        self.projection = decomposition.PCA(
                n_components = self.num_components)

    def fit(self, instances, quick = False):
        UnsupervisedProjection.fit(self, instances, quick = quick)
        if not quick:
            self.printExplainedVarianceCSV()
            self.printCumuledExplainedVarianceCSV()

    def transform(self, instances, quick = False):
        projected_instances = UnsupervisedProjection.transform(self, instances, quick = quick)
        if not quick:
            self.printReconstructionErrorsCSV(instances, projected_instances)
        return projected_instances

    def setProjectionMatrix(self):
        self.projection_matrix = np.transpose(
            self.pipeline.named_steps['projection'].components_)

    def setNumComponents(self):
        self.num_components = self.pipeline.named_steps['projection'].n_components_
    
    ######################
    # Explained Variance #
    ######################

    def printExplainedVarianceCSV(self):
        explained_var = pd.DataFrame(self.projection.explained_variance_ratio_,
                index = range(self.num_components),
                columns = ['y'])
        explained_var.index.name = 'x'
        explained_var.to_csv(
                self.outputFilename('explained_variance', '.csv'),
                sep = ',',
                header = True,
                index = True)

    def printCumuledExplainedVarianceCSV(self):
        explained_var = pd.DataFrame(
                np.cumsum(self.projection.explained_variance_ratio_),
                index = range(self.num_components),
                columns = ['y'])
        explained_var.index.name = 'x'
        explained_var.to_csv(
                self.outputFilename('cumuled_explained_variance', '.csv'),
                sep = ',',
                header = True,
                index = True)
    
    ########################
    # Reconstruction Error #
    ########################
    
    def printReconstructionErrorsCSV(self, instances, projected_instances):
        reconstruction_errors = pd.DataFrame(
                range(self.num_components),
                index = range(self.num_components),
                columns = ['y'])
        reconstruction_errors.index.name = 'x'
        for c in range(self.num_components):
            reconstruction_error = self.reconstructionError(
                    instances, projected_instances,c+1)
            reconstruction_errors.loc[c, 'y'] = reconstruction_error
        reconstruction_errors.to_csv(
            self.outputFilename('reconstruction_errors', '.csv'),
            sep = ',',
            header = True,
            index = True)
    
    def getReconstructedData(self, projected_instances, projection_size):
        projection = copy.deepcopy(projected_instances.getFeatures(
            num_max_features = projection_size))
        projection_matrix = np.transpose(
                self.projection_matrix[:, range(projection_size)])
        reconstructed_data = projection.dot(projection_matrix)
        return reconstructed_data

    def reconstructionError(self, instances, projected_instances, projection_size):
        reconstructed_data = self.getReconstructedData(projected_instances, 
                projection_size)
        reconstruction_error = 0
        diff = reconstructed_data - instances.features
        for i in range(instances.numInstances()):
            reconstruction_error += np.sum([x*x for x in diff[i,:]])
        reconstruction_error /= instances.numInstances()
        return reconstruction_error
