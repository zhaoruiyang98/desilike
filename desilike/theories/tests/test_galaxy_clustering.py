import numpy as np

from desilike import setup_logging


def test_integ():
    from desilike.theories.galaxy_clustering.base import BaseTheoryPowerSpectrumMultipolesFromWedges
    from desilike.theories.galaxy_clustering import StandardPowerSpectrumTemplate, KaiserTracerPowerSpectrumMultipoles

    topoles = BaseTheoryPowerSpectrumMultipolesFromWedges(mu=8)
    mu, wmu = topoles.mu, topoles.wmu
    assert np.isclose(np.sum(wmu), 1.)
    template = StandardPowerSpectrumTemplate()
    pk_trapz = KaiserTracerPowerSpectrumMultipoles(template=template, mu=100, method='trapz')()
    pk_leggauss = KaiserTracerPowerSpectrumMultipoles(template=template, mu=20, method='leggauss')()
    print(pk_trapz)
    print(pk_leggauss)


def test_templates():

    from desilike.theories.galaxy_clustering.power_template import PowerSpectrumInterpolator1D, integrate_sigma_r2, kernel_gauss2, kernel_gauss2_deriv, kernel_tophat2, kernel_tophat2_deriv

    from cosmoprimo.fiducial import DESI
    cosmo = DESI()
    pk = cosmo.get_fourier().pk_interpolator().to_1d(z=0.)
    r = 8.
    assert np.allclose(pk.sigma_r(r), integrate_sigma_r2(r, pk, kernel=kernel_tophat2)**0.5, atol=0., rtol=1e-3)
    """
    from matplotlib import pyplot as plt
    x = np.linspace(0., 0.2, 100)
    plt.plot(x, kernel_tophat2(x))
    plt.plot(x, kernel_tophat2_deriv(x))
    plt.show()
    """
    k = np.logspace(-2, 1, 100)
    n = -2.
    pk = PowerSpectrumInterpolator1D(k=k, pk=k**n)
    r = 1.
    """
    slope_gauss = integrate_sigma_r2(r, pk, kernel=kernel_gauss2_deriv) / integrate_sigma_r2(r, pk, kernel=kernel_gauss2)
    from scipy import special
    ntot = 2 + n
    print((2. * np.pi**2) * integrate_sigma_r2(r, pk, kernel=kernel_gauss2), special.gamma((ntot + 1) / 2.) / 2.)
    ntot_deriv = ntot + 1
    print((2. * np.pi**2) * integrate_sigma_r2(r, pk, kernel=kernel_gauss2_deriv) / (-2.), special.gamma((ntot_deriv + 1) / 2.) / 2.)
    print(slope_gauss / (-2.), special.gamma((ntot_deriv + 1) / 2.) / special.gamma((ntot + 1) / 2.))
    """
    slope_gauss = integrate_sigma_r2(r, pk, kernel=kernel_gauss2_deriv) / integrate_sigma_r2(r, pk, kernel=kernel_gauss2)
    slope_tophat = integrate_sigma_r2(r, pk, kernel=kernel_tophat2_deriv) / integrate_sigma_r2(r, pk, kernel=kernel_tophat2)
    print(slope_gauss, slope_tophat)

    from desilike.theories.galaxy_clustering.power_template import find_turn_over
    pk = cosmo.get_fourier().pk_interpolator().to_1d(z=0.)
    kTO, pkTO = find_turn_over(pk)
    k, k0 = np.logspace(-3, 1, 100), 0.01
    logk, logk0 = np.log10(k), np.log10(k0)
    pk = PowerSpectrumInterpolator1D(k=k, pk=10**(-(logk - logk0)**2))
    kTO, pkTO = find_turn_over(pk)
    assert np.allclose([kTO, pkTO], [k0, 1.])

    from desilike.theories.galaxy_clustering import KaiserTracerPowerSpectrumMultipoles, DampedBAOWigglesTracerPowerSpectrumMultipoles
    from desilike.theories.galaxy_clustering import (FixedPowerSpectrumTemplate, DirectPowerSpectrumTemplate, BAOPowerSpectrumTemplate,
                                                     StandardPowerSpectrumTemplate, ShapeFitPowerSpectrumTemplate, WiggleSplitPowerSpectrumTemplate,
                                                     BandVelocityPowerSpectrumTemplate, TurnOverPowerSpectrumTemplate, DirectWiggleSplitPowerSpectrumTemplate)

    for template in [BAOPowerSpectrumTemplate(), FixedPowerSpectrumTemplate(), ShapeFitPowerSpectrumTemplate(), DirectPowerSpectrumTemplate(), DirectWiggleSplitPowerSpectrumTemplate()]:
        theory = DampedBAOWigglesTracerPowerSpectrumMultipoles(template=template)
        theory()

    theory = DampedBAOWigglesTracerPowerSpectrumMultipoles(template=BAOPowerSpectrumTemplate(apmode='bao'))
    theory()
    assert 'n_s' in theory.varied_params

    from desilike.theories import Cosmoprimo
    cosmo = Cosmoprimo(fiducial='DESI')
    cosmo.init.params = {'Omega_m': {'prior': {'limits': [0.01, 0.9]}}}
    theory = DampedBAOWigglesTracerPowerSpectrumMultipoles(template=BAOPowerSpectrumTemplate(cosmo=cosmo, apmode='bao'))
    theory()
    assert 'n_s' not in theory.varied_params

    for template in [FixedPowerSpectrumTemplate(), DirectPowerSpectrumTemplate(), BAOPowerSpectrumTemplate(),
                     StandardPowerSpectrumTemplate(), ShapeFitPowerSpectrumTemplate(), ShapeFitPowerSpectrumTemplate(apmode='qisoqap'),
                     WiggleSplitPowerSpectrumTemplate(), WiggleSplitPowerSpectrumTemplate(kernel='tophat'), DirectWiggleSplitPowerSpectrumTemplate(),
                     BandVelocityPowerSpectrumTemplate(kp=np.linspace(0.01, 0.1, 10)), TurnOverPowerSpectrumTemplate()]:
        print(template)
        theory = KaiserTracerPowerSpectrumMultipoles(template=template)
        theory()
        template.f, template.f0
        template.init.update(only_now=True)
        theory = KaiserTracerPowerSpectrumMultipoles(template=template)
        theory()

    from desilike.theories.galaxy_clustering import BAOExtractor, StandardPowerSpectrumExtractor, ShapeFitPowerSpectrumExtractor, WiggleSplitPowerSpectrumExtractor, BandVelocityPowerSpectrumExtractor, TurnOverPowerSpectrumExtractor
    extractor = ShapeFitPowerSpectrumExtractor()
    dm = 0.02
    assert np.allclose(extractor(n_s=0.96 + dm).dm - extractor(n_s=0.96).dm, dm, atol=0., rtol=1e-5)
    for extractor in [BAOExtractor(), StandardPowerSpectrumExtractor(),
                      ShapeFitPowerSpectrumExtractor(), ShapeFitPowerSpectrumExtractor(dfextractor='fsigmar'),
                      WiggleSplitPowerSpectrumExtractor(), WiggleSplitPowerSpectrumExtractor(kernel='tophat'),
                      BandVelocityPowerSpectrumExtractor(kp=np.linspace(0.01, 0.1, 10)), TurnOverPowerSpectrumExtractor()]:
        extractor()


def test_wiggle_split_template():

    from matplotlib import pyplot as plt
    from desilike.theories.galaxy_clustering import DirectWiggleSplitPowerSpectrumTemplate

    fig, lax = plt.subplots(1, 2, sharex=False, sharey=True, figsize=(10, 4), squeeze=True)
    fig.subplots_adjust(wspace=0.25)

    for iname, (name, values) in enumerate(zip(['qbao', 'sigmabao'], [np.linspace(0.8, 1.2, 5), np.linspace(0., 10., 5)])):
        template = DirectWiggleSplitPowerSpectrumTemplate(k=np.linspace(0.001, 0.3, 100))
        template.init.params['sigmabao'].update(fixed=False)
        template()
        ax = lax[iname]
        cmap = plt.get_cmap('jet', len(values))
        ax.set_title(template.all_params[name].latex(inline=True))
        ax.plot(template.k, template.k * template.pk_dd, color='k')
        for ivalue, value in enumerate(values):
            template(**{name: value})
            ax.plot(template.k, template.k * template.pk_dd, color=cmap(ivalue / len(values)))
        ax.grid(True)
        ax.set_xlabel(r'$k$ [$h/\mathrm{Mpc}$]')
        ax.set_ylabel(r'$k P_{\ell}(k)$ [$(\mathrm{Mpc}/h)^{2}$]')
    plt.show()


def test_emulator_templates():
    from desilike.theories.galaxy_clustering import KaiserTracerPowerSpectrumMultipoles, DampedBAOWigglesTracerPowerSpectrumMultipoles
    calculator = DirectPowerSpectrumTemplate()
    theory = DampedBAOWigglesTracerPowerSpectrumMultipoles(template=calculator)
    theory()

    from desilike.emulators import Emulator, TaylorEmulatorEngine

    emulator = Emulator(calculator, engine=TaylorEmulatorEngine(order=1))
    emulator.set_samples()
    emulator.fit()
    calculator = emulator.to_calculator()
    calculator()

    theory.init.update(template=calculator, broadband='pcs')
    theory()

    theory = KaiserTracerPowerSpectrumMultipoles(template=calculator)
    theory()


def test_bao():

    from desilike.theories.galaxy_clustering import SimpleBAOWigglesTracerPowerSpectrumMultipoles, DampedBAOWigglesTracerPowerSpectrumMultipoles, ResummedBAOWigglesTracerPowerSpectrumMultipoles, FlexibleBAOWigglesTracerPowerSpectrumMultipoles
    from desilike.theories.galaxy_clustering import SimpleBAOWigglesTracerCorrelationFunctionMultipoles, DampedBAOWigglesTracerCorrelationFunctionMultipoles, ResummedBAOWigglesTracerCorrelationFunctionMultipoles, FlexibleBAOWigglesTracerCorrelationFunctionMultipoles
    from desilike.theories.galaxy_clustering import BAOPowerSpectrumTemplate, DirectPowerSpectrumTemplate, StandardPowerSpectrumTemplate


    def test_theory(theory):
        is_power = 'Power' in theory.__class__.__name__
        list_params, list_remove = {}, {}
        list_params['power'] = {'al0_1': 1e3 if is_power else 1e-3}
        list_params['power3'] = {'al0_-1': 1e3 if is_power else 1e-3}
        list_params['even-power'] = {'al0_2': 1e-3}
        list_params['pcs'] = {'al0_2': 2.}
        list_params['pcs2'] = {'al0_2': 2.}
        list_remove['power'] = ['al0_-1']
        list_remove['even-power'] = ['al0_0']
        list_remove['pcs'] = ['al0_-1']
        if not is_power:
            list_params['pcs'].update({'bl0_2': 1e-3})
        theory.init.update(pt=None, template=BAOPowerSpectrumTemplate())
        for broadband in ['power', 'power3', 'pcs'] + (['even-power', 'pcs2'] if not is_power else []):
            theory.init.update(broadband=broadband)
            #print(theory.all_params)
            params = list_params[broadband]
            remove = list_remove.get(broadband, [])
            if broadband == 'power3':
                vp = theory.varied_params
                assert len(vp.names(basename=['al0_*'])) == 3, theory.varied_params
            if broadband == 'pcs2':
                vp = theory.varied_params
                assert len(vp.names(basename=['al0_*'])) == 0 and len(vp.names(basename=['al2_*'])) == 2, theory.varied_params
            for name, value in params.items():
                theory.init.params[name].update(fixed=True)
            for name in remove:
                del theory.init.params[name]
            for name in params:
                assert name not in theory.varied_params
            for name in remove:
                assert name not in theory.all_params
            namespace = 'LRG'
            for param in theory.init.params:
                param.update(namespace=namespace)
            print(theory.init.params)
            theory(qpar=1.1, **{namespace + '.' + param: value for param, value in params.items()})
            theory.z, theory.ells, theory.template
            if 'PowerSpectrum' in theory.__class__.__name__:
                theory.k
            else:
                theory.s
            theory.plot(show=False)
            template = BAOPowerSpectrumTemplate(z=0.1, fiducial='DESI', apmode='qiso', only_now=True)
            theory.init.update(template=template)
            theory(qiso=0.9)
            for param in theory.all_params.select(basename=['d', 'sigmapar', 'sigmaper', 'ml*_*']):
                assert param.fixed
            template = DirectPowerSpectrumTemplate(z=1., fiducial='DESI')
            theory.init.update(template=template)
            theory()
            template = StandardPowerSpectrumTemplate(z=1., fiducial='DESI', with_now='peakaverage')
            theory.init.update(template=template)
            theory()
            template.pk_dd
            for param in theory.init.params: param.update(namespace='LRG')
            basenames = theory.init.params.basenames()
            theory()
            for param in theory.all_params:
                if param.basename in basenames:
                    assert param.namespace == 'LRG'

    def test_emulate(theory, emulate='pt'):
        for template in [BAOPowerSpectrumTemplate(z=1., fiducial='DESI', with_now='peakaverage'),
                         DirectPowerSpectrumTemplate(z=1., fiducial='DESI'),
                         StandardPowerSpectrumTemplate(z=1., fiducial='DESI', with_now='peakaverage')]:
            theory.init.update(template=template)
            theory()

            from desilike.emulators import Emulator, TaylorEmulatorEngine

            bak = theory(**{param.name: param.value for param in theory.all_params.select(input=True)})
            if 'PowerSpectrum' in theory.__class__.__name__: theory.k
            else: theory.s
            if emulate == 'pt': calculator = theory.pt
            else: calculator = theory
            emulator = Emulator(calculator, engine=TaylorEmulatorEngine(order=1))
            emulator.set_samples()
            emulator.fit()
            calculator = emulator.to_calculator()
            if emulate == 'pt':
                theory.init.update(pt=calculator)
            else:
                theory = calculator
            print(emulate, theory.init.params.basenames())
            assert np.allclose(theory(), bak)


    def test(theory):
        test_emulate(theory)
        test_theory(theory)

    theory = DampedBAOWigglesTracerPowerSpectrumMultipoles(ells=(0,))
    assert 'dbeta' in theory.all_params
    assert 'dbeta' not in theory.varied_params

    theory = FlexibleBAOWigglesTracerCorrelationFunctionMultipoles()
    assert 'dbeta' in theory.all_params
    assert 'dbeta' not in theory.varied_params

    theory = DampedBAOWigglesTracerCorrelationFunctionMultipoles()
    theory(sigmas=3.)
    fig = theory.plot()
    theory(sigmas=6.)
    theory.plot(fig=fig, show=True)

    test(SimpleBAOWigglesTracerPowerSpectrumMultipoles())
    test(DampedBAOWigglesTracerPowerSpectrumMultipoles())
    test(ResummedBAOWigglesTracerPowerSpectrumMultipoles())
    test(FlexibleBAOWigglesTracerPowerSpectrumMultipoles())

    test(SimpleBAOWigglesTracerCorrelationFunctionMultipoles())
    test(DampedBAOWigglesTracerCorrelationFunctionMultipoles())
    test(ResummedBAOWigglesTracerCorrelationFunctionMultipoles())
    test(FlexibleBAOWigglesTracerCorrelationFunctionMultipoles())


def test_flexible_bao():

    from matplotlib import pyplot as plt

    from desilike.theories.galaxy_clustering import FlexibleBAOWigglesTracerPowerSpectrumMultipoles, FlexibleBAOWigglesTracerCorrelationFunctionMultipoles

    if False:
        fig, lax = plt.subplots(1, 2, sharex=False, sharey=True, figsize=(10, 4), squeeze=True)
        fig.subplots_adjust(wspace=0.25)
        theory = FlexibleBAOWigglesTracerPowerSpectrumMultipoles(ells=(0,), broadband='pcs', wiggles='pcs')
        for iax, mode in enumerate(['additive', 'multiplicative']):
            ax = lax[iax]
            for ill, ell in enumerate(theory.ells):
                names = theory.varied_params.names(basename='{}l{:d}_*'.format(mode[0], ell))
                cmap = plt.get_cmap('jet', len(names))
                for iname, name in enumerate(names):
                    pk = theory(**{name: 1.})
                    ax.plot(theory.k, theory.k * pk[ill], color=cmap(iname / len(names)))
                    pk = theory(**{name: 0.})
                ax.plot(theory.k, theory.k * pk[ill], color='k')
            ax.grid(True)
            ax.set_xlabel(r'$k$ [$h/\mathrm{Mpc}$]')
            ax.set_ylabel(r'$k P_{\ell}(k)$ [$(\mathrm{Mpc}/h)^{2}$]')
            ax.set_title(mode)
        plt.show()

    if True:
        fig, lax = plt.subplots(1, 2, sharex=False, sharey=True, figsize=(10, 4), squeeze=True)
        fig.subplots_adjust(wspace=0.25)
        theory = FlexibleBAOWigglesTracerCorrelationFunctionMultipoles(ells=(0, 2), broadband='pcs', wiggles='pcs')
        for iax, mode in enumerate(['additive', 'multiplicative']):
            ax = lax[iax]
            for ill, ell in enumerate(theory.ells):
                names = theory.varied_params.names(basename=['{}l{:d}_[-1:1]'.format(prefix, ell) for prefix in (['a', 'b'][:1] if mode == 'additive' else ['m'])])
                cmap = plt.get_cmap('jet', len(names))
                for iname, name in enumerate(names):
                    xi = theory(**{name: 1e-3 if name.startswith('b') else 1e3})
                    ax.plot(theory.s, theory.s**2 * xi[ill], color=cmap(iname / len(names)))
                    xi = theory(**{name: 0.})
                    ax.plot(theory.s, theory.s**2 * xi[ill], color='k')
            ax.grid(True)
            ax.set_xlabel(r'$s$ [$\mathrm{Mpc}/h$]')
            ax.set_ylabel(r'$s^{2} \xi_{\ell}(s)$ [$(\mathrm{Mpc}/h)^{2}$]')
            ax.set_title(mode)
        plt.show()


def test_broadband_bao():

    from matplotlib import pyplot as plt

    from desilike.theories.galaxy_clustering import DampedBAOWigglesTracerPowerSpectrumMultipoles, DampedBAOWigglesTracerCorrelationFunctionMultipoles

    if True:
        ax = plt.gca()
        theory = DampedBAOWigglesTracerPowerSpectrumMultipoles(ells=(0, 2), k=np.linspace(0.001, 0.4, 100), broadband='pcs')
        for ill, ell in enumerate(theory.ells):
            names = theory.varied_params.names(basename='al{:d}_*'.format(ell))
            cmap = plt.get_cmap('jet', len(names))
            for iname, name in enumerate(names):
                pk = theory(**{name: 1.})
                ax.plot(theory.k, theory.k * pk[ill], color=cmap(iname / len(names)))
                pk = theory(**{name: 0.})
            ax.plot(theory.k, theory.k * pk[ill], color='k')
        ax.grid(True)
        ax.set_xlabel(r'$k$ [$h/\mathrm{Mpc}$]')
        ax.set_ylabel(r'$k P_{\ell}(k)$ [$(\mathrm{Mpc}/h)^{2}$]')
        plt.show()

    if False:
        ax = plt.gca()
        theory = DampedBAOWigglesTracerCorrelationFunctionMultipoles(ells=(0, 2), broadband='pcs')
        for ill, ell in enumerate(theory.ells):
            names = theory.varied_params.names(basename=['{}l{:d}_[-1:1]'.format(prefix, ell) for prefix in ['a', 'b']][:1])
            print(names)
            cmap = plt.get_cmap('jet', len(names))
            for iname, name in enumerate(names):
                xi = theory(**{name: 1e-3 if name.startswith('b') else 1e3})
                ax.plot(theory.s, theory.s**2 * xi[ill], color=cmap(iname / len(names)))
                xi = theory(**{name: 0.})
                ax.plot(theory.s, theory.s**2 * xi[ill], color='k')
        ax.grid(True)
        ax.set_xlabel(r'$s$ [$\mathrm{Mpc}/h$]')
        ax.set_ylabel(r'$s^{2} \xi_{\ell}(s)$ [$(\mathrm{Mpc}/h)^{2}$]')
        plt.show()

    if False:
        fig, lax = plt.subplots(1, 2, sharex=False, sharey=True, figsize=(10, 4), squeeze=True)
        fig.subplots_adjust(wspace=0.25)

        def get_analytic(s, delta):
            from scipy.special import sici
            x = delta * s
            sinx, cosx, cos2x = np.sin(x), np.cos(x), np.cos(2 * x)
            Si_x, Si_2x = sici(x)[0], sici(2 * x)[0]
            poly = {}
            poly['al2_-1'] = (16.0 - 8.0 * x**2 - 16.0 * cosx + x**2 * cosx - x * sinx + x**3 * Si_x) / (2.0 * x**3 * s**3)
            poly['al2_0'] = -2.0 * (12.0 - 16 * cosx + x**2 * cosx + 4.0 * cos2x - x**2 * cos2x - x * sinx + x * cosx * sinx + x**3 * Si_x - 2.0 * x**3 * Si_2x) / (x**3 * s**3)
            return poly

        theory = DampedBAOWigglesTracerCorrelationFunctionMultipoles(s=np.linspace(1., 130., 130), ells=(0, 2), broadband='pcs')
        for ill, ell in enumerate(theory.ells):
            ax = lax[ill]
            names = theory.varied_params.names(basename=['{}l{:d}_[-1:1]'.format(prefix, ell) for prefix in ['a', 'b']][:1])
            print(names)
            cmap = plt.get_cmap('jet', len(names))
            for iname, name in enumerate(names):
                xiref = theory(**{name: 0.})
                xi = theory(**{name: 1e-3 if name.startswith('b') else 1.})
                diff = xi[ill] - xiref[ill]
                color = cmap(iname / len(names))
                ax.plot(theory.s, theory.s**2 * diff, color=color)
                analytic = get_analytic(theory.s, delta=theory.power.kp)
                if name in analytic:
                    ratio = diff[-1] / analytic[name][-1]
                    ax.plot(theory.s, theory.s**2 * analytic[name] * ratio, color=color, linestyle='--')
                xi = theory(**{name: 0.})
            ax.grid(True)
            ax.set_xlabel(r'$s$ [$\mathrm{Mpc}/h$]')
            ax.set_ylabel(r'$s^{2} \xi_{\ell}(s)$ [$(\mathrm{Mpc}/h)^{2}$]')
        plt.show()


def test_full_shape():

    from desilike.theories.galaxy_clustering import LPTVelocileptorsTracerPowerSpectrumMultipoles, PyBirdTracerPowerSpectrumMultipoles, FOLPSTracerPowerSpectrumMultipoles
    from desilike.theories.galaxy_clustering import LPTVelocileptorsTracerCorrelationFunctionMultipoles, PyBirdTracerCorrelationFunctionMultipoles, FOLPSTracerCorrelationFunctionMultipoles

    def clean_folps():
        import FOLPSnu as FOLPS
        import types
        for name, value in FOLPS.__dict__.items():
            if not name.startswith('__') and not callable(value) and not isinstance(value, types.ModuleType):
                FOLPS.__dict__[name] = None

    def test(theory, test_likelihood=True, emulate='pt', show=False):
        if test_likelihood:
            from desilike.observables.galaxy_clustering import TracerPowerSpectrumMultipolesObservable, TracerCorrelationFunctionMultipolesObservable, ObservablesCovarianceMatrix
            from desilike.likelihoods import ObservablesGaussianLikelihood
            ells = (0, 2, 4)
            if 'Power' in theory.__class__.__name__:
                observable = TracerPowerSpectrumMultipolesObservable(klim={ell: [0.05, 0.2, 0.01] for ell in ells},
                                                                     data={}, theory=theory)
            else:
                observable = TracerCorrelationFunctionMultipolesObservable(slim={ell: [20, 150, 4] for ell in ells},
                                                                           data={}, theory=theory)
            observable()
            theory.plot(show=show)
            cov = np.eye(observable.flatdata.shape[0])
            likelihood = ObservablesGaussianLikelihood(observables=[observable], covariance=cov)
            for param in likelihood.all_params.select(basename=['alpha*', 'sn*', 'c*']):
                param.update(derived='.best')
            for param in likelihood.all_params.select(basename=['alpha6']):
                param.update(fixed=True)
            likelihood()
            theory.z, theory.ells, theory.template
            clean_folps()
        from desilike.emulators import Emulator, TaylorEmulatorEngine

        bak = theory(**{param.name: param.value for param in theory.all_params.select(input=True)})
        if 'PowerSpectrum' in theory.__class__.__name__: theory.k
        else: theory.s
        if emulate == 'pt': calculator = theory.pt
        else: calculator = theory
        emulator = Emulator(calculator, engine=TaylorEmulatorEngine(order=0))
        emulator.set_samples()
        emulator.fit()
        calculator = emulator.to_calculator()
        if emulate == 'pt':
            theory.init.update(pt=calculator)
        else:
            theory = calculator
        clean_folps()
        assert np.allclose(theory(), bak)
        theory.z, theory.ells
        if 'PowerSpectrum' in theory.__class__.__name__:
            theory.k, theory.nd
        else:
            theory.s
        if test_likelihood:
            #observable.init.update(theory=theory)
            for param in likelihood.all_params.select(basename=['alpha*', 'sn*', 'c*']):
                param.update(derived='.best')
            likelihood()
            print(likelihood.all_params.select(solved=True))
            from desilike.theories.galaxy_clustering.base import BaseTheoryCorrelationFunctionFromPowerSpectrumMultipoles
            if not isinstance(theory, BaseTheoryCorrelationFunctionFromPowerSpectrumMultipoles):
                theory.plot(show=show)
        for param in theory.init.params: param.update(namespace='LRG')
        basenames = theory.init.params.basenames()
        theory()
        for param in theory.all_params:
            if param.basename in basenames:
                assert param.namespace == 'LRG'
        for param in theory.init.params: param.update(namespace=None)

    from desilike.theories.galaxy_clustering import ShapeFitPowerSpectrumTemplate

    ntemplate = 4
    for TheoryPower, TheoryCorr in zip([LPTVelocileptorsTracerPowerSpectrumMultipoles, PyBirdTracerPowerSpectrumMultipoles, FOLPSTracerPowerSpectrumMultipoles],
                                       [LPTVelocileptorsTracerCorrelationFunctionMultipoles, PyBirdTracerCorrelationFunctionMultipoles, FOLPSTracerCorrelationFunctionMultipoles]):
        for freedom in [None, 'min', 'max'][2:]:
            for ells in [(0, 2), (0, 2, 4)]:
                print(freedom, ells)
                power = TheoryPower(ells=ells, freedom=freedom)
                print(TheoryPower.__name__, ells, freedom, power.varied_params)
                if freedom is not None: assert len(power.varied_params) == ntemplate + 6 + (4 in ells) + 2 * (freedom == 'max')  # 2 (+ 2) bias, 2 (+ 1) EFT, 2 sn
                corr = TheoryCorr(ells=ells, freedom=freedom)
                print(TheoryCorr.__name__, ells, freedom, corr.varied_params)
                if freedom is not None: assert len(corr.varied_params) == ntemplate + 4 + (4 in ells) + 2 * (freedom == 'max')  # 2 (+ 2) bias, 2 EFT
                for param in corr.varied_params:
                    assert param in power.varied_params, '{} not in {}'.format(param, power.varied_params)
                for theory in [power, corr]:
                    for param in theory.init.params: param.update(namespace='LRG')
                    basenames = theory.init.params.basenames()
                    theory()
                    for param in theory.all_params:
                        if param.basename in basenames:
                            assert param.namespace == 'LRG'
                if 'velocileptors' in TheoryPower.__name__.lower() and freedom == 'max':
                    for name in ['LRG.b2', 'LRG.bs', 'LRG.b3']:
                        assert theory.all_params[name].prior.dist == 'uniform'

    from desilike.theories.galaxy_clustering import ShapeFitPowerSpectrumTemplate
    from desilike.theories.galaxy_clustering import SimpleTracerPowerSpectrumMultipoles
    theory = SimpleTracerPowerSpectrumMultipoles()
    test(theory, emulate=None)

    from desilike.theories.galaxy_clustering import KaiserTracerPowerSpectrumMultipoles, KaiserTracerCorrelationFunctionMultipoles
    theory = KaiserTracerPowerSpectrumMultipoles()
    theory()
    test(theory, emulate='pt')
    test(theory, emulate=None, test_likelihood=False)
    theory = KaiserTracerCorrelationFunctionMultipoles()
    test(theory, emulate='pt')
    test(theory, emulate=None, test_likelihood=False)

    from desilike.theories.galaxy_clustering import EFTLikeKaiserTracerPowerSpectrumMultipoles, EFTLikeKaiserTracerCorrelationFunctionMultipoles

    theory = EFTLikeKaiserTracerPowerSpectrumMultipoles(template=ShapeFitPowerSpectrumTemplate(z=1.))
    theory()
    test(theory, emulate='pt')
    theory(df=1.01, b1=1., sn2_2=1., sigmapar=4.).shape
    test(theory, emulate=None, test_likelihood=False)
    theory(df=1.01, b1=1., sn2_2=1., sigmapar=4.).shape

    theory = EFTLikeKaiserTracerCorrelationFunctionMultipoles(template=ShapeFitPowerSpectrumTemplate(z=0.5, apmode='qisoqap'))
    test(theory)
    theory(df=1.01, b1=1., ct0_2=1.).shape

    from desilike.theories.galaxy_clustering import TNSTracerPowerSpectrumMultipoles, TNSTracerCorrelationFunctionMultipoles

    theory = TNSTracerPowerSpectrumMultipoles(template=ShapeFitPowerSpectrumTemplate(z=0.5))
    test(theory, emulate='pt')
    theory(df=1.01, b1=1.).shape
    test(theory, emulate=None, test_likelihood=False)
    theory(df=1.01, b1=1.).shape

    theory = TNSTracerCorrelationFunctionMultipoles(template=ShapeFitPowerSpectrumTemplate(z=0.5))
    test(theory)
    theory(df=1.01, b1=1., b2=1.).shape

    from desilike.theories.galaxy_clustering import EFTLikeTNSTracerPowerSpectrumMultipoles, EFTLikeTNSTracerCorrelationFunctionMultipoles

    if False:
        #k = np.logspace(-3, 1.5, 1000)
        k = np.linspace(0.01, 0.3, 60)
        theory = EFTLikeKaiserTracerPowerSpectrumMultipoles(k=k, ells=(0, 2), template=ShapeFitPowerSpectrumTemplate(z=1.))
        theory()
        theory_tns = EFTLikeTNSTracerPowerSpectrumMultipoles(k=k, ells=(0, 2), template=ShapeFitPowerSpectrumTemplate(z=1.))
        theory_tns()

        from matplotlib import pyplot as plt

        from pyregpt import A1Loop, B1Loop

        pyregpt = A1Loop()
        pyregpt.set_pk_lin(theory_tns.template.k, theory_tns.template.pk_dd)
        pyregpt.set_terms(theory_tns.pt.k)
        pyregpt.run_terms(nthreads=4)

        ax = plt.gca()
        for i in range(5):
            ax.plot(pyregpt['k'], pyregpt['pk'][:, i], color='C{:d}'.format(i), linestyle='-', label='regpt' if i == 0 else None)
            ax.plot(theory_tns.pt.k, theory_tns.pt._A[i, :, 0], color='C{:d}'.format(i), linestyle='--', label='desilike' if i == 0 else None)
        ax.legend()
        plt.show()
        exit()

        pyregpt = B1Loop()
        pyregpt.set_pk_lin(theory_tns.template.k, theory_tns.template.pk_dd)
        pyregpt.set_terms(theory_tns.pt.k)
        pyregpt.run_terms(nthreads=4)

        ax = plt.gca()
        for i in range(9):
            ax.plot(pyregpt['k'], pyregpt['pk'][:, i], color='C{:d}'.format(i), linestyle='-', label='regpt' if i == 0 else None)
            ax.plot(theory_tns.pt.k, theory_tns.pt._B[i, :, 0], color='C{:d}'.format(i), linestyle='--', label='desilike' if i == 0 else None)
        ax.legend()
        plt.show()
        exit()

        from pyregpt import Bias1Loop

        pyregpt = Bias1Loop()
        pyregpt.set_pk_lin(theory_tns.template.k, theory_tns.template.pk_dd)
        pyregpt.set_terms(theory_tns.pt.k11)
        pyregpt.run_terms(nthreads=4)

        ax = plt.gca()
        #for name in ['pk11', 'pk_dd', 'pk_b2d', 'pk_bs2d', 'pk_sig3sq', 'pk_b22', 'pk_b2s2', 'pk_bs22', 'pk_dt', 'pk_b2t', 'pk_bs2t', 'pk_tt']:
        for i, name in enumerate(['pk_b2d', 'pk_bs2d', 'pk_sig3sq', 'pk_b22', 'pk_b2s2', 'pk_bs22', 'pk_b2t', 'pk_bs2t']):
            ax.plot(theory_tns.pt.k11, np.abs(getattr(theory_tns.pt, name)), color='C{:d}'.format(i), linestyle='-', label=name)
            if name == 'pk_sig3sq':
                regptpk = pyregpt.pk_sigma3sq()
            else:
                regptpk = pyregpt[name]
            ax.plot(pyregpt['k'], np.abs(regptpk), color='C{:d}'.format(i), linestyle='--')
            #ax.plot(pyregpt['k'], np.abs(getattr(theory_tns.pt, name)) / np.abs(regptpk), color='C{:d}'.format(i), linestyle='--')
        ax.set_yscale('log')
        ax.legend()
        plt.show()

        fig, lax = plt.subplots(1, 2, sharey=True)
        lax = lax.flatten()
        for ax, name in zip(lax, ['A', 'B']):
            print(theory_tns.pt.pktable[name].shape)
            corr = np.sum(theory_tns.pt.pktable[name], axis=0)
            for ill, ell in enumerate(theory.ells):
                ax.plot(theory_tns.pt.k, corr[ill] / theory.power[ill], color='C{:d}'.format(ill))
        plt.show()

        ax = plt.gca()
        mask = k < 0.3
        for ill, ell in enumerate(theory.ells):
            ax.plot(theory.k[mask], theory.k[mask] * theory.power[ill][mask], color='C{:d}'.format(ill))
            ax.plot(theory_tns.k[mask], theory_tns.k[mask] * theory_tns.power[ill][mask], color='C{:d}'.format(ill), linestyle='--')
        plt.show()

    theory = EFTLikeTNSTracerPowerSpectrumMultipoles(template=ShapeFitPowerSpectrumTemplate(z=0.5))

    test(theory, emulate='pt')
    theory(df=1.01, b1=1.).shape
    test(theory, emulate=None, test_likelihood=False)
    theory(df=1.01, b1=1.).shape

    theory = EFTLikeTNSTracerCorrelationFunctionMultipoles(template=ShapeFitPowerSpectrumTemplate(z=0.5))
    test(theory)
    theory(df=1.01, b1=1., ct0_2=1.).shape

    from desilike.theories.galaxy_clustering import LPTVelocileptorsTracerPowerSpectrumMultipoles, LPTVelocileptorsTracerCorrelationFunctionMultipoles
    theory = LPTVelocileptorsTracerPowerSpectrumMultipoles(template=ShapeFitPowerSpectrumTemplate(z=0.5))
    theory(dm=0.01, b1=1.).shape
    assert not np.allclose(theory(dm=-0.01), theory(dm=0.01))
    assert not np.allclose(theory(qpar=0.99), theory(qper=1.01))
    test(theory, emulate='pt')
    test(theory, emulate=None, test_likelihood=False)
    theory = LPTVelocileptorsTracerCorrelationFunctionMultipoles(ells=(0, 2), template=ShapeFitPowerSpectrumTemplate(z=0.5))
    test(theory)
    theory(dm=0.01, b1=1.).shape
    theory.pt

    from desilike.theories.galaxy_clustering import EPTMomentsVelocileptorsTracerPowerSpectrumMultipoles, EPTMomentsVelocileptorsTracerCorrelationFunctionMultipoles
    theory = EPTMomentsVelocileptorsTracerPowerSpectrumMultipoles(template=ShapeFitPowerSpectrumTemplate(z=0.5))
    test(theory)
    theory(dm=0.01, b1=1.).shape
    theory = EPTMomentsVelocileptorsTracerCorrelationFunctionMultipoles(ells=(0, 2), template=ShapeFitPowerSpectrumTemplate(z=0.5))
    test(theory)
    theory(dm=0.01, b1=1.).shape
    theory.pt

    from desilike.theories.galaxy_clustering import LPTMomentsVelocileptorsTracerPowerSpectrumMultipoles, LPTMomentsVelocileptorsTracerCorrelationFunctionMultipoles
    theory = LPTMomentsVelocileptorsTracerPowerSpectrumMultipoles(template=ShapeFitPowerSpectrumTemplate(z=0.5))
    test(theory)
    theory(dm=0.01, b1=1.).shape
    theory = LPTMomentsVelocileptorsTracerCorrelationFunctionMultipoles(ells=(0, 2), template=ShapeFitPowerSpectrumTemplate(z=0.5))
    test(theory)
    theory(dm=0.01, b1=1.).shape
    theory.pt

    from desilike.theories.galaxy_clustering import PyBirdTracerPowerSpectrumMultipoles, PyBirdTracerCorrelationFunctionMultipoles

    for freedom in ['min', 'max', None]:
        print(freedom)
        theory = PyBirdTracerPowerSpectrumMultipoles(freedom=freedom)
        test(theory)
        theory(logA=3.04, b1=1.).shape
        theory = PyBirdTracerCorrelationFunctionMultipoles(freedom=freedom)
        test(theory)  # no P(k) computed
        theory(logA=3.04, b1=1.).shape

    from desilike.theories.galaxy_clustering import FOLPSTracerPowerSpectrumMultipoles, FOLPSTracerCorrelationFunctionMultipoles

    theory = FOLPSTracerPowerSpectrumMultipoles()
    test(theory)
    theory(logA=3.04, b1=1.).shape

    theory = FOLPSTracerCorrelationFunctionMultipoles()
    test(theory)  # no P(k) computed
    theory(logA=3.04, b1=1.).shape


def test_velocileptors():
    from desilike.theories.galaxy_clustering import DirectPowerSpectrumTemplate, LPTVelocileptorsTracerPowerSpectrumMultipoles, LPTVelocileptorsTracerCorrelationFunctionMultipoles
    z = 0.5
    template = DirectPowerSpectrumTemplate(z=z)
    k = np.arange(0.005, 0.3, 0.01)
    theory = LPTVelocileptorsTracerPowerSpectrumMultipoles(template=template, k=k, shotnoise=1.)
    biases = [0.71, 0.26, 0.67, 0.52]
    cterms = [-3.4, -1.7, 6.5, 0]
    stoch = [1500., -1900., 0]
    pars = biases + cterms + stoch
    names = ['b1', 'b2', 'bs', 'b3', 'alpha0', 'alpha2', 'alpha4', 'alpha6', 'sn0', 'sn2', 'sn4']
    power = theory(**dict(zip(names, pars)))

    from velocileptors.LPT.lpt_rsd_fftw import LPT_RSD
    options = dict(kIR=0.2, cutoff=10, extrap_min=-5, extrap_max=3, N=4000, threads=1, jn=5)
    lpt = LPT_RSD(template.k, template.pk_dd, **options)
    lpt.make_pltable(template.f, kv=k, nmax=4, apar=1, aperp=1)
    ref = lpt.combine_bias_terms_pkell(pars)[1:]

    from matplotlib import pyplot as plt
    ax = plt.gca()
    for ill, ell in enumerate((0, 2, 4)):
        ax.plot(k, k * ref[ill], color='C{:d}'.format(ill), ls='-', label=r'$\ell = {:d}$'.format(ell))
        ax.plot(k, k * power[ill], color='C{:d}'.format(ill), ls='--')
        #ax.plot(k, k * (ref[ill] / power[ill] - 1.), color='C{:d}'.format(ill), ls='-', label=r'$\ell = {:d}$'.format(ell))
    ax.set_xlim([k[0], k[-1]])
    ax.grid(True)
    ax.legend()
    ax.set_ylabel(r'$k \Delta P_{\ell}(k)$ [$(\mathrm{Mpc}/h)^{2}$]')
    ax.set_xlabel(r'$k$ [$h/\mathrm{Mpc}$]')
    plt.show()

    stoch = [0, 0, 0]
    pars = biases + cterms + stoch
    lpt.make_pltable(template.f, apar=1, aperp=1, kmin=5e-3, kmax=1.0, nk=60, nmax=4)
    ref = lpt.combine_bias_terms_xiell(pars)
    s = ref[0][0]
    s = s[(s > 0.) & (s < 150.)]
    theory = LPTVelocileptorsTracerCorrelationFunctionMultipoles(template=template, s=s)
    corr = theory(**dict(zip(names, pars)))

    ax = plt.gca()
    for ill, ell in enumerate((0, 2, 4)):
        ax.plot(ref[ill][0], ref[ill][0]**2 * ref[ill][1], color='C{:d}'.format(ill), ls='-', label=r'$\ell = {:d}$'.format(ell))
        ax.plot(s, s**2 * corr[ill], color='C{:d}'.format(ill), ls='--')
    ax.set_xlim([s[0], s[-1]])
    ax.set_ylim(-80., 80.)
    ax.grid(True)
    ax.legend()
    ax.set_ylabel(r'$s^{2} \Delta \xi_{\ell}(s)$ [$(\mathrm{Mpc}/h)^{2}$]')
    ax.set_xlabel(r'$s$ [$\mathrm{Mpc}/h$]')
    plt.show()


def test_pybird():
    from matplotlib import pyplot as plt
    from desilike.theories.galaxy_clustering import DirectPowerSpectrumTemplate, PyBirdTracerPowerSpectrumMultipoles, PyBirdTracerCorrelationFunctionMultipoles
    z = 0.5
    template = DirectPowerSpectrumTemplate(z=z)
    with_nnlo_counterterm = True
    shotnoise = 1e4

    k = np.arange(0.005, 0.3, 0.01)
    #k = np.arange(0.0001, 0.3, 0.01)
    theory = PyBirdTracerPowerSpectrumMultipoles(template=template, eft_basis='eftoflss', k=k, shotnoise=shotnoise, km=0.7, kr=0.35, with_nnlo_counterterm=with_nnlo_counterterm)
    theory()
    kk, pk_lin, psmooth, f = template.k, template.pk_dd, template.pknow_dd, template.f
    eft_params = {'b1': 1.9535, 'b3': -0.3948, 'cct': 0.1839, 'cr1': -0.8414, 'cr2': -0.8084,
                  'ce0': 1.5045, 'ce1': 0.0, 'ce2': -1.6803, 'b2': 0.4146, 'b4': 0.4146, 'cr4': 10., 'cr6': 20.}
    from pybird.correlator import Correlator
    c = Correlator()
    c.set({'output': 'bPk', 'multipole': 3, 'kmax': k[-1] * 1.2, 'xdata': k, 'with_bias': False, 'optiresum': False,
           'km': 0.7, 'kr': 0.35, 'nd': 1. / shotnoise, 'eft_basis': 'eftoflss', 'with_stoch': True, 'with_nnlo_counterterm': with_nnlo_counterterm})
    c.compute({'kk': kk, 'pk_lin': pk_lin, 'Psmooth': psmooth, 'f': f})
    ref = c.get(eft_params)
    #c.compute({'kk': kk, 'pk_lin': pk_lin, 'Psmooth': psmooth, 'f': f, 'bias': eft_params})
    #ref = c.get()
    power = theory(**eft_params)
    print(power[:, :3])  # difference comes from the AP projection
    print(ref[:, :3])

    ax = plt.gca()
    for ill, ell in enumerate((0, 2, 4)):
        ax.plot(k, k * ref[ill], color='C{:d}'.format(ill), ls='-', label=r'$\ell = {:d}$'.format(ell))
        ax.plot(k, k * power[ill], color='C{:d}'.format(ill), ls='--')
        #ax.plot(k, k * (ref[ill] / power[ill] - 1.), color='C{:d}'.format(ill), ls='-', label=r'$\ell = {:d}$'.format(ell))
    ax.set_xlim([k[0], k[-1]])
    ax.grid(True)
    ax.legend()
    ax.set_ylabel(r'$k \Delta P_{\ell}(k)$ [$(\mathrm{Mpc}/h)^{2}$]')
    ax.set_xlabel(r'$k$ [$h/\mathrm{Mpc}$]')
    plt.show()

    for eft_basis in ['westcoast', 'eastcoast']:
        theory.init.update(eft_basis=eft_basis)
        theory()

    s = np.arange(10, 200, 5.)
    template = DirectPowerSpectrumTemplate(z=z)
    theory = PyBirdTracerCorrelationFunctionMultipoles(template=template, eft_basis='eftoflss', s=s, km=0.7, kr=0.35, with_nnlo_counterterm=with_nnlo_counterterm)
    corr = theory()
    kk, pk_lin, psmooth, f = template.k, template.pk_dd, template.pknow_dd, template.f
    from pybird.correlator import Correlator
    c = Correlator()
    c.set({'output': 'bCf', 'multipole': 3, 'kmax': 0.25, 'xdata': s, 'with_bias': False,
           'km': 0.7, 'kr': 0.35, 'nd': 1. / shotnoise, 'eft_basis': 'eftoflss', 'with_stoch': True, 'with_nnlo_counterterm': with_nnlo_counterterm})
    c.compute({'kk': kk, 'pk_lin': pk_lin, 'Psmooth': psmooth, 'f': f})
    eft_params = {'b1': 1.9535, 'b3': -0.3948, 'cct': 0.1839, 'cr1': -0.8414, 'cr2': -0.8084,
                  'b2': 0.4146, 'b4': 0.4146, 'cr4': 10., 'cr6': 20.}
    ref = c.get(eft_params)
    #c.compute({'kk': kk, 'pk_lin': pk_lin, 'Psmooth': psmooth, 'f': f, 'bias': eft_params})
    #ref = c.get()
    corr = theory(**eft_params)
    print(corr[:, :3])
    print(ref[:, :3])

    ax = plt.gca()
    for ill, ell in enumerate((0, 2, 4)):
        ax.plot(s, s**2 * ref[ill], color='C{:d}'.format(ill), ls='-', label=r'$\ell = {:d}$'.format(ell))
        ax.plot(s, s**2 * corr[ill], color='C{:d}'.format(ill), ls='--')
    ax.set_xlim([s[0], s[-1]])
    ax.grid(True)
    ax.legend()
    ax.set_ylabel(r'$s^{2} \Delta \xi_{\ell}(s)$ [$(\mathrm{Mpc}/h)^{2}$]')
    ax.set_xlabel(r'$s$ [$\mathrm{Mpc}/h$]')
    plt.show()

    for eft_basis in ['westcoast', 'eastcoast']:
        theory.init.update(eft_basis=eft_basis)
        theory()


def test_folps():
    from matplotlib import pyplot as plt
    z_pk = 0.5
    k = np.logspace(np.log10(0.01), np.log10(0.3), num=50) # array of k_ev in [h/Mpc]
    PshotP = 1. / 0.0002118763
    # bias parameters
    b1 = 1.645
    b2 = -0.46
    bs2 = -4./7*(b1 - 1)
    b3nl = 32./315*(b1 - 1)
    # EFT parameters
    alpha0 = 3                 #units: [Mpc/h]^2
    alpha2 = -28.9             #units: [Mpc/h]^2
    alpha4 = 0.0               #units: [Mpc/h]^2
    ctilde = 0.0               #units: [Mpc/h]^4
    # Stochatics parameters
    alphashot0 = 0.08
    alphashot2 = -8.1          #units: [Mpc/h]^2
    NuisanParams = [b1, b2, bs2, b3nl, alpha0, alpha2, alpha4, ctilde, alphashot0, alphashot2, PshotP]

    from desilike.theories.galaxy_clustering import DirectPowerSpectrumTemplate, FOLPSTracerPowerSpectrumMultipoles, FOLPSTracerCorrelationFunctionMultipoles
    template = DirectPowerSpectrumTemplate(z=z_pk)
    theory = FOLPSTracerPowerSpectrumMultipoles(template=template, k=k, shotnoise=PshotP, mu=3)

    for m_ncdm in [0.2, 0.5]:
        theory(m_ncdm=m_ncdm)
        cosmo = template.cosmo
        omega_b, omega_cdm, omega_ncdm, h = cosmo['omega_b'], cosmo['omega_cdm'], cosmo['omega_ncdm_tot'], cosmo['h']
        CosmoParams = [z_pk, omega_b, omega_cdm, omega_ncdm, h]
        inputpkT = [template.k, template.pk_dd]

        import FOLPSnu as FOLPS
        matrices = FOLPS.Matrices()
        nonlinear = FOLPS.NonLinear(inputpkT, CosmoParams)
        ref = FOLPS.RSDmultipoles(k, NuisanParams, AP=False)[1:]
        print(theory.template.f0 / FOLPS.f0)
        power = theory(b1=b1, b2=b2, bs=bs2 + 4./7*(b1 - 1), b3=b3nl - 32./315*(b1 - 1),
                    alpha0=alpha0, alpha2=alpha2, alpha4=alpha4, ct=ctilde, sn0=alphashot0, sn2=alphashot2)

        ax = plt.gca()
        for ill, ell in enumerate((0, 2, 4)):
            ax.plot(k, k * ref[ill], color='C{:d}'.format(ill), ls='-', label=r'$\ell = {:d}$'.format(ell))
            ax.plot(k, k * power[ill], color='C{:d}'.format(ill), ls='--')
            #ax.plot(k, k * (ref[ill] / power[ill] - 1.), color='C{:d}'.format(ill), ls='-', label=r'$\ell = {:d}$'.format(ell))
        ax.set_xlim([k[0], k[-1]])
        ax.grid(True)
        ax.legend()
        ax.set_ylabel(r'$k \Delta P_{\ell}(k)$ [$(\mathrm{Mpc}/h)^{2}$]')
        ax.set_xlabel(r'$k$ [$h/\mathrm{Mpc}$]')
        plt.show()

    theory = FOLPSTracerCorrelationFunctionMultipoles()
    theory()
    theory.plot(show=True)


def test_params():

    from desilike.theories.galaxy_clustering import KaiserTracerPowerSpectrumMultipoles, KaiserTracerCorrelationFunctionMultipoles
    theory = KaiserTracerPowerSpectrumMultipoles()
    for param in theory.init.params:
        param.update(namespace='LRG')
    print(theory.all_params)
    print(theory.runtime_info.pipeline.param_values)

    theory = KaiserTracerCorrelationFunctionMultipoles()
    for param in theory.init.params:
        param.update(namespace='LRG')
    print(theory.all_params)


def test_png():

    from desilike.theories.galaxy_clustering import PNGTracerPowerSpectrumMultipoles, ShapeFitPowerSpectrumTemplate

    theory = PNGTracerPowerSpectrumMultipoles(method='prim')
    params = dict(fnl_loc=100., b1=2.)
    theory2 = PNGTracerPowerSpectrumMultipoles(method='matter')
    assert np.allclose(theory2(**params), theory(**params), rtol=2e-3)
    assert not np.allclose(theory2(fnl_loc=0.), theory(), rtol=2e-3)

    theory = PNGTracerPowerSpectrumMultipoles(template=ShapeFitPowerSpectrumTemplate(z=1.), method='prim')
    theory(qpar=1.1, fnl_loc=2.)
    theory.plot(show=True)

    from desilike.emulators import Emulator, TaylorEmulatorEngine
    emulator = Emulator(theory, engine=TaylorEmulatorEngine(order=1))
    emulator.set_samples()
    emulator.fit()
    calculator = emulator.to_calculator()
    calculator(qpar=1.1, fnl_loc=2.)


from scipy import special
from desilike import utils
from desilike.jax import numpy as jnp
from desilike.theories.galaxy_clustering import DirectPowerSpectrumTemplate, APEffect
from desilike.theories.galaxy_clustering import KaiserTracerPowerSpectrumMultipoles
from desilike.theories.galaxy_clustering.full_shape import BaseTheoryCorrelationFunctionFromPowerSpectrumMultipoles


class CorrelationFunctionMultipoles(BaseTheoryCorrelationFunctionFromPowerSpectrumMultipoles):

    config_fn = None

    def initialize(self, *args, pt=None, template=None, mu=20, method='leggauss', **kwargs):
        #power = globals()[self.__class__.__name__.replace('CorrelationFunction', 'PowerSpectrum')]()
        power = KaiserTracerPowerSpectrumMultipoles()
        if pt is not None: power.init.update(pt=pt)
        if template is None:
            template = DirectPowerSpectrumTemplate()
        power.init.update(template=template)
        super(CorrelationFunctionMultipoles, self).initialize(*args, power=power, **kwargs)
        self.apeffect = power.template.apeffect
        power.template.runtime_info.requires = [require for require in power.template.runtime_info.requires if require is not self.apeffect]
        power.template.apeffect = APEffect(mode='qparqper')
        power.template.apeffect()
        self.mu, wmu = utils.weights_mu(mu, method=method)
        self.legendre = [special.legendre(ell) for ell in self.ells]
        self.wmu = np.array([wmu * (2 * ell + 1) * leg(self.mu) for ell, leg in zip(self.ells, self.legendre)])

    def calculate(self):
        power = []
        for pk in self.power.power:
            slope_high = (pk[-1] - pk[-2]) / np.log10(self.kin[-1] / self.kin[-2])
            power.append(jnp.concatenate([jnp.interp(np.log10(self.k_mid), np.log10(self.kin), pk), (pk[-1] + slope_high * self.k_high) * self.pad_high], axis=-1))
        s, corr = self.fftlog(np.vstack(power))
        sap, muap = self.apeffect.ap_s_mu(self.s, self.mu)[1:]
        self.corr = jnp.array([jnp.sum(jnp.interp(sap, ss, cc) * leg(muap) * wmu, axis=-1) for ss, cc, leg, wmu in zip(s, corr, self.legendre, self.wmu)])

    @property
    def pt(self):
        return self.power.pt

    @property
    def template(self):
        return self.power.template

    def get(self):
        return self.corr


def test_pk_to_xi():
    from matplotlib import pyplot as plt
    from desilike.theories.galaxy_clustering import ShapeFitPowerSpectrumTemplate
    from desilike.theories.galaxy_clustering import (KaiserTracerPowerSpectrumMultipoles, LPTVelocileptorsTracerPowerSpectrumMultipoles, PyBirdTracerPowerSpectrumMultipoles,
                                                     EPTMomentsVelocileptorsTracerPowerSpectrumMultipoles, LPTMomentsVelocileptorsTracerPowerSpectrumMultipoles)
    from desilike.emulators import Emulator, TaylorEmulatorEngine

    from cosmoprimo import PowerToCorrelation

    k = np.logspace(-4., 3., 2048)
    ells = (0, 2, 4)

    for Theory in [KaiserTracerPowerSpectrumMultipoles, LPTVelocileptorsTracerPowerSpectrumMultipoles,
                   EPTMomentsVelocileptorsTracerPowerSpectrumMultipoles, LPTMomentsVelocileptorsTracerPowerSpectrumMultipoles]:
        fftlog = PowerToCorrelation(k, ell=ells, q=0, lowring=True)
        theory = Theory(template=ShapeFitPowerSpectrumTemplate(z=1.1))
        theory.init.update(k=np.geomspace(k[0], 1., 300), ells=ells)

        def interp(k, kin, pk):
            mask = k > kin[-1]
            k_high = np.log10(k[mask] / kin[-1])
            pad_high = np.exp(-(k[mask] / kin[-1] - 1.)**2 / (2. * (10.)**2))
            slope_high = (pk[-1] - pk[-2]) / np.log10(kin[-1] / kin[-2])
            k_mid = k[~mask]
            return np.concatenate([np.interp(np.log10(k_mid), np.log10(kin), pk), (pk[-1] + slope_high * k_high) * pad_high], axis=-1)

        fig, lax = plt.subplots(1, 2, sharex=False, sharey=False, figsize=(10, 6), squeeze=True)
        fig.subplots_adjust(hspace=0)
        pk = theory()
        pk = [interp(k, theory.k, pk) for pk in pk]
        s, xi = fftlog(pk)
        for ill, ell in enumerate(theory.ells):
            lax[0].plot(k, pk[ill], color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
            #mask = (k > 0.01) & (k < 0.3)
            #lax[0].plot(k[mask], k[mask] * pk[ill][mask], color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
            si = s[ill]
            mask = (si > 1.) & (si < 200.)
            lax[1].plot(si[mask], si[mask]**2 * xi[ill][mask], color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
        lax[0].legend()
        lax[0].set_xscale('log')
        #lax[0].set_xscale('linear')
        lax[1].set_xscale('linear')
        plt.show()
    """
    theory = CorrelationFunctionMultipoles(s=np.linspace(1., 200., 1000), template=ShapeFitPowerSpectrumTemplate(z=1.1))
    ax = plt.gca()
    xi_ref = theory()
    for qpar in [0.999, 1., 1.001]:
        xi = theory(qpar=qpar)
        for ill, ell in enumerate(theory.ells):
            ax.plot(theory.s, theory.s**2 * (xi[ill] - xi_ref[ill]), color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
    plt.show()

    theory = CorrelationFunctionMultipoles(template=ShapeFitPowerSpectrumTemplate(z=1.1))
    #print(theory.all_params)
    #theory.all_params['b1'].update(fixed=True)
    theory.all_params['df'].update(fixed=True)
    calculator = theory
    emulator = Emulator(calculator, engine=TaylorEmulatorEngine(order=3))
    emulator.set_samples(method='finite', accuracy=4)
    emulator.fit()
    calculator = emulator.to_calculator()
    ax = plt.gca()
    for qpar, dm, df in [(0.95, -0.05, 0.95), (1., 0., 1.), (1.05, 0.05, 1.05)]:
        params = dict(qpar=qpar, dm=0., df=1.)
        #params = dict(qpar=1., dm=dm, df=1.)
        #params = dict(qpar=1., dm=0., df=df)
        xi = theory(**params)
        for ill, ell in enumerate(theory.ells):
            ax.plot(theory.s, theory.s**2 * xi[ill], color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
        xi = calculator(**params)
        for ill, ell in enumerate(calculator.ells):
            ax.plot(calculator.s, calculator.s**2 * xi[ill], color='C{:d}'.format(ill), linestyle='--')
    plt.show()
    """


def test_ap_diff():

    from matplotlib import pyplot as plt
    from desilike.theories.galaxy_clustering import (BAOPowerSpectrumTemplate, ShapeFitPowerSpectrumTemplate,
                                                     DampedBAOWigglesTracerCorrelationFunctionMultipoles, ResummedBAOWigglesTracerCorrelationFunctionMultipoles,
                                                     KaiserTracerPowerSpectrumMultipoles, KaiserTracerCorrelationFunctionMultipoles,
                                                     PyBirdTracerPowerSpectrumMultipoles, PyBirdTracerCorrelationFunctionMultipoles,
                                                     LPTVelocileptorsTracerPowerSpectrumMultipoles, LPTVelocileptorsTracerCorrelationFunctionMultipoles,
                                                     EPTMomentsVelocileptorsTracerPowerSpectrumMultipoles, EPTMomentsVelocileptorsTracerCorrelationFunctionMultipoles,
                                                     LPTMomentsVelocileptorsTracerPowerSpectrumMultipoles, LPTMomentsVelocileptorsTracerCorrelationFunctionMultipoles)
    from desilike.emulators import Emulator, TaylorEmulatorEngine
    for Theory in [KaiserTracerPowerSpectrumMultipoles, PyBirdTracerPowerSpectrumMultipoles, LPTVelocileptorsTracerPowerSpectrumMultipoles,
                   EPTMomentsVelocileptorsTracerPowerSpectrumMultipoles, LPTMomentsVelocileptorsTracerPowerSpectrumMultipoles][2:]:
        fig, lax = plt.subplots(2, sharex=True, sharey=False, figsize=(10, 6), squeeze=True)
        fig.subplots_adjust(hspace=0)
        theory = Theory(template=ShapeFitPowerSpectrumTemplate(z=1.1))
        pk_ref = theory()
        for ill, ell in enumerate(theory.ells):
            lax[0].plot(theory.k, theory.k * pk_ref[ill], color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
        for qpar in [0.998, 1., 1.002]:
            pk = theory(qpar=qpar)
            for ill, ell in enumerate(theory.ells):
                lax[1].plot(theory.k, theory.k * (pk[ill] - pk_ref[ill]), color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
        plt.show()

    for Theory in [DampedBAOWigglesTracerCorrelationFunctionMultipoles, ResummedBAOWigglesTracerCorrelationFunctionMultipoles]:
        theory = Theory(s=np.linspace(10., 200., 1000), template=BAOPowerSpectrumTemplate(z=1.1))
        xi_ref = theory()
        fig, lax = plt.subplots(2, sharex=True, sharey=False, figsize=(10, 6), squeeze=True)
        fig.subplots_adjust(hspace=0)
        ax = plt.gca()
        for ill, ell in enumerate(theory.ells):
            lax[0].plot(theory.s, theory.s**2 * xi_ref[ill], color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
        for qpar in [0.998, 1., 1.002]:
            xi = theory(qpar=qpar)
            for ill, ell in enumerate(theory.ells):
                lax[1].plot(theory.s, theory.s**2 * (xi[ill] - xi_ref[ill]), color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
        plt.show()

    # For pybird, chat with Pierre Zhang
    for Theory in [KaiserTracerCorrelationFunctionMultipoles, LPTVelocileptorsTracerCorrelationFunctionMultipoles,
                   PyBirdTracerCorrelationFunctionMultipoles, EPTMomentsVelocileptorsTracerCorrelationFunctionMultipoles,
                   LPTMomentsVelocileptorsTracerCorrelationFunctionMultipoles]:
        theory = Theory(s=np.linspace(10., 200., 1000), template=ShapeFitPowerSpectrumTemplate(z=1.1))
        xi_ref = theory()
        if hasattr(theory, 'plot'):
            theory.plot(show=True)
        fig, lax = plt.subplots(2, sharex=True, sharey=False, figsize=(10, 6), squeeze=True)
        fig.subplots_adjust(hspace=0)
        ax = plt.gca()
        for ill, ell in enumerate(theory.ells):
            lax[0].plot(theory.s, theory.s**2 * xi_ref[ill], color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
        for qpar in [0.998, 1., 1.002]:
            xi = theory(qpar=qpar)
            for ill, ell in enumerate(theory.ells):
                lax[1].plot(theory.s, theory.s**2 * (xi[ill] - xi_ref[ill]), color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
        plt.show()

    theory = KaiserTracerPowerSpectrumMultipoles(template=ShapeFitPowerSpectrumTemplate(z=1.1))
    theory.all_params['b1'].update(fixed=True)
    theory.all_params['df'].update(fixed=True)
    calculator = theory
    emulator = Emulator(calculator, engine=TaylorEmulatorEngine(order=4))
    emulator.set_samples(method='finite', accuracy=4)
    emulator.fit()
    calculator = emulator.to_calculator()
    ax = plt.gca()
    for qpar, dm, df in [(0.95, -0.05, 0.95), (1., 0., 1.), (1.05, 0.05, 1.05)]:
        params = dict(qpar=qpar, dm=0., df=1.)
        #params = dict(qpar=1., dm=dm, df=1.)
        #params = dict(qpar=1., dm=0., df=df)
        pk = theory(**params)
        for ill, ell in enumerate(theory.ells):
            ax.plot(theory.k, theory.k * pk[ill], color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
        pk = calculator(**params)
        for ill, ell in enumerate(calculator.ells):
            ax.plot(calculator.k, calculator.k * pk[ill], color='C{:d}'.format(ill), linestyle='--')
    plt.show()

    theory = KaiserTracerCorrelationFunctionMultipoles(template=ShapeFitPowerSpectrumTemplate(z=1.1))
    #theory.all_params['b1'].update(fixed=True)
    #theory.all_params['df'].update(fixed=True)
    calculator = theory
    emulator = Emulator(calculator, engine=TaylorEmulatorEngine(order=3))
    emulator.set_samples(method='finite')
    emulator.fit()
    calculator = emulator.to_calculator()
    ax = plt.gca()
    for qpar, dm, df in [(0.95, -0.05, 0.95), (1., 0., 1.), (1.05, 0.05, 1.05)]:
        params = dict(qpar=qpar, dm=0., df=1.)
        #params = dict(qpar=1., dm=dm, df=1.)
        #params = dict(qpar=1., dm=0., df=df)
        xi = theory(**params)
        for ill, ell in enumerate(theory.ells):
            ax.plot(theory.s, theory.s**2 * xi[ill], color='C{:d}'.format(ill), label=r'$\ell = {:d}$'.format(ell))
        xi = calculator(**params)
        for ill, ell in enumerate(calculator.ells):
            ax.plot(calculator.s, calculator.s**2 * xi[ill], color='C{:d}'.format(ill), linestyle='--')
    plt.show()


def test_ptt():

    from desilike.theories.galaxy_clustering import BandVelocityPowerSpectrumTemplate, KaiserTracerPowerSpectrumMultipoles, BandVelocityPowerSpectrumCalculator
    z = 1.
    theory = KaiserTracerPowerSpectrumMultipoles(template=BandVelocityPowerSpectrumTemplate(kp=np.linspace(0.01, 0.1, 10), z=z))
    power = BandVelocityPowerSpectrumCalculator(calculator=theory)
    print(power().shape, power.varied_params)


if __name__ == '__main__':

    setup_logging()

    #test_velocileptors()
    #test_pybird()
    #test_folps()
    #test_params()
    #test_integ()
    #test_templates()
    #test_wiggle_split_template()
    #test_emulator_templates()
    #test_bao()
    #test_broadband_bao()
    #test_flexible_bao()
    test_full_shape()
    #test_png()
    #test_pk_to_xi()
    #test_ap_diff()
    #test_ptt()