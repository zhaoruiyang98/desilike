import os

from desilike.theories.galaxy_clustering import (KaiserTracerPowerSpectrumMultipoles, LPTVelocileptorsTracerPowerSpectrumMultipoles,
                                                 DirectPowerSpectrumTemplate, ShapeFitPowerSpectrumTemplate)
from desilike.emulators.base import Emulator, EmulatedCalculator
from desilike import setup_logging


def test_base():
    emulator_dir = '_tests'
    fn = os.path.join(emulator_dir, 'emu.npy')

    for Template in [DirectPowerSpectrumTemplate, ShapeFitPowerSpectrumTemplate]:
        calculator = KaiserTracerPowerSpectrumMultipoles(template=Template())
        calculator.all_params['b1'].update(derived='{b}**2', prior=None)
        calculator.all_params['b'] = {'prior': {'limits': [0., 2.]}}

        emulator = Emulator(calculator, engine='point')
        emulator.set_samples()
        emulator.fit()
        emulator.save(fn)
        calculator = emulator.to_calculator()

        emulator = EmulatedCalculator.load(fn)
        emulator.runtime_info.initialize()
        #print(emulator.runtime_info.varied_params)
        #print(emulator.runtime_info.param_values)
        print(emulator.varied_params, emulator.all_params)
        print(emulator.runtime_info.pipeline.get_cosmo_requires())
        emulator()
        emulator = emulator.deepcopy()
        #print(emulator.params, emulator.runtime_info.init[2], emulator.runtime_info.params)
        emulator().shape
        emulator.save(fn)

        emulator = EmulatedCalculator.load(fn)

    calculator = LPTVelocileptorsTracerPowerSpectrumMultipoles(template=ShapeFitPowerSpectrumTemplate())
    calculator()
    pt = calculator.pt
    emulator = Emulator(pt, engine='point')
    emulator.set_samples()
    emulator.fit()
    emulator.save(fn)
    pt = EmulatedCalculator.load(fn)
    calculator.init.update(pt=pt)
    calculator(df=0.8)


if __name__ == '__main__':

    setup_logging()
    test_base()
