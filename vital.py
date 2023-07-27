from ..grain import Grain
from .. import geometry
from ..simResult import SimAlert, SimAlertLevel, SimAlertType
from ..properties import FloatProperty, EnumProperty

class BellShapedGrain(Grain):
    """A bell-shaped grain is designed with a gradually decreasing burning area (inner surface) to achieve the desired thrust profile."""
    geomName = "Bell-Shaped"

    def __init__(self):
        super().__init__()
        # Add properties specific to the Bell-Shaped grain
        self.props['initialPortDiameter'] = FloatProperty('Initial Port Diameter', 'm', 0, 1)
        self.props['throatDiameter'] = FloatProperty('Throat Diameter', 'm', 0, 1)
        self.props['aftEndDiameter'] = FloatProperty('Aft End Diameter', 'm', 0, 1)
        self.props['inhibitedEnds'] = EnumProperty('Inhibited Ends', ['Both'])

    def isCoreInverted(self):
        """A simple helper that returns 'true' if the core's forward diameter is larger than its aft diameter"""
        return self.props['initialPortDiameter'].getValue() > self.props['aftEndDiameter'].getValue()

    # Implement methods specific to the Bell-Shaped grain
    def getFrustumInfo(self, regDist):
        """Returns the dimensions of the grain's core at a given regression depth. The core is always a frustum and is
        returned as the aft diameter, forward diameter, and length"""
        initialPortDiameter = self.props['initialPortDiameter'].getValue()
        throatDiameter = self.props['throatDiameter'].getValue()
        aftEndDiameter = self.props['aftEndDiameter'].getValue()
        grainLength = self.props['length'].getValue()

        exposedFaces = 0
        inhibitedEnds = self.props['inhibitedEnds'].getValue()
        if inhibitedEnds == 'Neither':
            exposedFaces = 2
        elif inhibitedEnds in ['Top', 'Bottom']:
            exposedFaces = 1

        # These calculations are easiest if we work in terms of the core's "large end" and "small end"
        if self.isCoreInverted():
            coreMajorDiameter, coreMinorDiameter = initialPortDiameter, aftEndDiameter
        else:
            coreMajorDiameter, coreMinorDiameter = aftEndDiameter, initialPortDiameter

        # Calculate the half angle of the core. This is done with without accounting for regression because it doesn't
        # change with regression
        angle = atan((coreMajorDiameter - coreMinorDiameter) / (2 * grainLength))

        # Adjust core dimensions to achieve the desired thrust profile
        regCoreMajorDiameter = coreMajorDiameter * (1 - regDist / grainLength)
        regCoreMinorDiameter = coreMinorDiameter * (1 - regDist / grainLength)

        # Calculate frustum length and diameter at the regression distance
        frustumLength = grainLength - regDist
        aftFrustumDiameter = regCoreMinorDiameter
        forwardFrustumDiameter = regCoreMajorDiameter

        if self.isCoreInverted():
            return aftFrustumDiameter, forwardFrustumDiameter, frustumLength

        return forwardFrustumDiameter, aftFrustumDiameter, frustumLength

    def getMassFlux(self, massIn, dTime, regDist, dRegDist, position, density):
        """Returns the mass flux at a point along the grain. Takes in the mass flow into the grain, a timestep, the
        distance the grain has regressed so far, the additional distance it will regress during the timestep, a
        position along the grain measured from the head end, and the density of the propellant."""

        # Calculate core dimensions at current and future regression distances
        currentDiameters = self.getFrustumInfo(regDist)
        futureDiameters = self.getFrustumInfo(regDist + dRegDist)

        # Calculate mass flow rate based on core dimensions
        currentVolume = geometry.frustumVolume(*currentDiameters)
        futureVolume = geometry.frustumVolume(*futureDiameters)
        massFlow = (futureVolume - currentVolume) * density / dTime
        massFlow += massIn

        # Calculate port area based on core dimensions at current regression distance
        portDiameter = currentDiameters[1] if self.isCoreInverted() else currentDiameters[0]
        portArea = geometry.circleArea(portDiameter)

        return massFlow / portArea

    # Add other methods as needed

    def simulationSetup(self, config):
        """Do anything needed to prepare this grain for simulation"""
        return None

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        # Check for any specific geometry errors related to the Bell-Shaped grain
        # ...

        return errors
    
    when this repo exists 
