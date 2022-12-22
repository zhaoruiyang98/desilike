import numpy as np

from desilike import setup_logging
from desilike.install import Installer
from desilike.likelihoods.supernovae import PantheonSNLikelihood


def test_install():
    likelihood = PantheonSNLikelihood()
    installer = Installer(user=True)
    installer(likelihood)
    likelihood()
    assert np.allclose((likelihood + likelihood)(), 2. * likelihood())


if __name__ == '__main__':

    setup_logging()
    test_install()
