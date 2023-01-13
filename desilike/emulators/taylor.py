import itertools

import numpy as np

from desilike import mpi
from desilike.jax import numpy as jnp
from desilike.utils import expand_dict
from desilike.parameter import Deriv
from .base import BaseEmulatorEngine


class TaylorEmulatorEngine(BaseEmulatorEngine):

    name = 'taylor'
    _samples_with_derivs = True

    def initialize(self, varied_params, order=3, accuracy=2, ref_scale=0.5):
        self.varied_params = varied_params
        self.sampler_options = dict(order=order, accuracy=accuracy, ref_scale=ref_scale)

    def get_default_samples(self, calculator, **kwargs):
        from desilike import Differentiation
        options = {**self.sampler_options, **kwargs}
        differentiation = Differentiation(calculator, **options, mpicomm=self.mpicomm)
        return differentiation()

    def fit(self, X, Y):
        if self.mpicomm.bcast(Y.derivs is None if self.mpicomm.rank == 0 else None, root=0):
            raise ValueError('Please provide samples with derivatives computed')
        Y = Y[0]  # only need one element
        self.center, self.derivatives, self.powers = None, None, None
        if self.mpicomm.rank == 0:
            self.derivatives, self.powers = [], []
            self.center = np.array([np.median(np.unique(xx)) for xx in X.T])
            ndim = len(self.varied_params)
            max_order, max_param_order = 0, [0 for i in range(ndim)]
            for deriv in Y.derivs:
                for iparam, param in enumerate(self.varied_params):
                    max_param_order[iparam] = max(max_param_order[iparam], deriv[param])
                    max_order = max(max_order, deriv.total())
            prefactor, degrees = 1., []
            for order in range(0, max_order + 1):
                if order: prefactor /= order
                for indices in itertools.product(range(ndim), repeat=order):
                    powers = np.zeros(len(self.center), dtype='i4')
                    orders = np.bincount(indices, minlength=ndim).astype('i4')
                    if order and sum(orders) > min(order for o, order in zip(orders, max_param_order) if o):
                        continue
                    degree = Deriv(dict(zip(self.varied_params, orders)))
                    if degree not in Y.derivs:
                        import warnings
                        warnings.warn("Derivative {} is missing, let's assume it is 0".format(degree))
                        continue
                    value = prefactor * Y[degree]
                    if degree in degrees:
                        self.derivatives[degrees.index(degree)] += value
                    else:
                        degrees.append(degree)
                        self.powers.append(orders)
                        self.derivatives.append(value)
            self.derivatives, self.powers = np.array(self.derivatives), np.array(self.powers)
        self.derivatives = mpi.bcast(self.derivatives if self.mpicomm.rank == 0 else None, mpicomm=self.mpicomm, mpiroot=0)
        self.powers = self.mpicomm.bcast(self.powers, root=0)
        self.center = self.mpicomm.bcast(self.center, root=0)

    def predict(self, X):
        diffs = jnp.array(X - self.center)
        diffs = jnp.where(self.powers > 0, diffs, 0.)  # a trick to avoid NaNs in the derivation
        powers = jnp.prod(jnp.power(diffs, self.powers), axis=-1)
        return jnp.tensordot(self.derivatives, powers, axes=(0, 0))

    def __getstate__(self):
        state = {}
        for name in ['center', 'derivatives', 'powers']:
            state[name] = getattr(self, name)
        return state
