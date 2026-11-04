# Conversions for comparison

Preserve both original readings and original CRA cell strings. Use code/calculator arithmetic on values read by the agent; do not use automated plot/table extraction. Conversions establish comparability, not identity. Do not choose an electrode offset, composition basis, ingredient or constant by fitting a target. Record formulas, inputs, assumptions and authoritative constant sources in evidence or short shared notes. There is no bundled general unit parser or hard-coded universal electrode offset.

## Potentials and electrode references

With the same reference, `V × 1000 = mV`. For an affine reference conversion, express reference potentials against a common scale:

`E_vs_SCE = E_vs_source + E_source_vs_common - E_SCE_vs_common`.

Then convert volts to mV if necessary. Apply the scale and offset to central values and bound endpoints. Apply only the absolute scale factor to `plus_minus`; do not offset an uncertainty. Retain inequality direction and statistical meaning. Check arithmetic rather than inferring agreement from similarly sized values.

Use paper-supplied calibration where applicable, otherwise verify appropriate constants with an authoritative reference. Record filling solution and reference-electrode temperature/conditions. Experimental solution temperature need not equal reference-electrode temperature. Do not assume a universal SHE/SCE or Ag/AgCl/SCE offset. RHE conversion additionally requires pH and temperature. An unidentified quasi-reference cannot receive an offset fitted to Citrine.

Useful manufacturer references:

- [Gamry reference-electrode conversion resource](https://www.gamry.com/resources-2/electrochemical-calculators-tools/convert-potentials-to-another-reference-electrode/): distinguishes electrode types and filling solutions.
- [Gamry saturated calomel temperature calculator](https://www.gamry.com/resources-2/electrochemical-calculators-tools/saturated-calomel-electrode-calculator/): check applicable temperature conditions.

When necessary details are missing, label assumptions explicitly and keep numerical comparison conditional or `not_comparable`. Independent context can still establish identity; uncertainty in the conversion is not a reason to invent agreement. Do not turn repassivation, corrosion, applied potential or a current threshold into another physical quantity by unit conversion.

## Alloy composition

CRA element columns are wt%. Distinguish mass fraction, atomic fraction, wt%, at%, nominal composition and measured composition. Mass fraction × 100 gives wt%; atomic fraction × 100 gives at%.

With a sufficiently specified source composition and atomic masses `M_i`:

`w_i = x_i M_i / Σ_j(x_j M_j)`

`x_i = (w_i / M_i) / Σ_j(w_j / M_j)`.

Multiply fractions by 100 for percent. Document the complete composition and atomic-mass source. A stated binary balance can supply the remainder, labeled calculated. One at% solute in an unspecified multicomponent alloy cannot be converted uniquely to wt%. Do not fill missing paper composition from CRA and then call the result independent paper evidence. Converting CRA to source units is allowed if useful, but label it a dataset-derived calculation and preserve the original wt% value.

## Other association variables

- CRA test temperature is °C. Convert K by subtracting 273.15, or °F by `(F - 32) × 5/9`. Do not infer room temperature or other unstated conditions.
- CRA scan-rate header is mV/s, but its cell may be a number, `steady state`, or prose. `1 V/min = 1000/60 mV/s` only when the quantity is a genuine continuous sweep rate. A stated 20 mV step is not 20 mV/s. Read the procedure to distinguish sweep rates, potential increments and dwell times; potentiostatic labels alone do not resolve that meaning.
- CRA `CL- [M]` is molar chloride concentration. Derive concentrations only with sufficient species, concentration-basis, formula and volume/density information. Do not equate salt ppm with chloride ppm, molality with molarity, or unspecified normality with chloride molarity. Do not assume a standard seawater recipe or infer missing pH.
- pH is dimensionless. Preserve source-reported pH versus calculated values and their assumptions.

Judge numerical agreement by the source's rounding, plotting scale and marker resolution. Preserve signs and defensible precision. A visually read 0.30 V does not establish hundredth-millivolt precision because the CSV has many decimals. Do not manufacture a mean, interpolate a missing replicate, or treat numeric equality as proof that a censored or qualitative outcome is the same result.
