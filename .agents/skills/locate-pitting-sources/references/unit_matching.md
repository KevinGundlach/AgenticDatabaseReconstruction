# Unit conversions for matching

Conversions are comparison calculations, not replacements for the paper's observations or the CSV strings. Always retain both originals in the report. Do arithmetic with code/calculator where useful; local code may convert values already read visually, but must not extract observations from plots/tables. Never use the desired Citrine number to choose an offset, composition basis, missing ingredient or conversion constant.

## Potential scale and reference

First identify both the voltage unit and reference electrode. With the same reference, `V x 1000 = mV`; apply the same scale factor to endpoints and uncertainties. A voltage-unit conversion does not change the electrode reference.

For a justified reference change, with all potentials expressed in volts against a common reference (such as SHE):

`E_vs_SCE = E_vs_source + E_source_vs_common - E_SCE_vs_common`.

Then multiply by 1000 for mV (SCE). Document the offset values, their source, filling electrolyte and applicable reference-electrode temperature, and any approximation. Use a paper-supplied calibration/conversion if applicable, otherwise verify constants against an authoritative reference. A reference-electrode conversion is permitted matching work; do not reject an otherwise sound candidate merely because it needs one.

Do not silently assume a universal SHE/SCE or Ag/AgCl/SCE offset. The source reference and filling solution matter, and reference potentials vary with temperature. Test temperature does not necessarily equal reference-electrode temperature. If a required detail is unavailable, label a documented assumption explicitly and keep the resulting match conditional; if no defensible conversion can be made, report the location/context as a candidate but mark numerical comparison `Not comparable`. RHE conversion additionally needs pH and temperature information. An unidentified quasi-reference cannot be assigned a standard offset by fitting the database target.

Manufacturer resources for checking actual conversions and conditions:

- [Gamry reference-electrode conversion calculator](https://www.gamry.com/resources-2/electrochemical-calculators-tools/convert-potentials-to-another-reference-electrode/)
- [Gamry SCE temperature calculator](https://www.gamry.com/resources-2/electrochemical-calculators-tools/saturated-calomel-electrode-calculator/)

Do not convert corrosion, repassivation or imposed potential into pitting potential; these are different quantities regardless of units. Do not transform a single observation into a mean, a range into error bars, or a current threshold into a pitting event to match a database label.

## Composition basis

Distinguish mass fraction, wt%, atomic fraction, at%, and nominal versus measured compositions. Same-looking percentages with different bases are not directly equal. Mass fraction x 100 gives wt%; atomic fraction x 100 gives at%.

When a complete source composition is known, convert using atomic masses `M_i` and fractions:

- Atomic to mass fraction: `w_i = x_i M_i / sum_j(x_j M_j)`.
- Mass to atomic fraction: `x_i = (w_i / M_i) / sum_j(w_j / M_j)`.

Multiply the resulting fraction by 100 to express percent. Document the atomic-mass source and which complete composition was used in a shared conversion note. A binary alloy with a reported balance can supply its remainder for comparison, explicitly labeled calculated. A single Nb at% value in an otherwise unspecified multicomponent alloy is insufficient for conversion to wt%. Do not fill source-composition gaps using Citrine and then claim the reconstructed composition is independent supporting evidence. Prefer comparing Citrine converted into source units if that avoids inventing source inputs, but label it a dataset-derived calculation rather than a reported paper value, and retain the original CSV amount in wt%.

## Other supporting variables and agreement

Convert only what is needed to identify the target: e.g. K to degC (subtract 273.15), mass-concentration units with known formula/molar mass, or molarity from a stated recipe when all necessary quantities are available. Mark derived concentration as calculated, not reported. Do not equate molality with molarity without the needed density information, assume a seawater recipe, or infer missing pH. Normality is reaction/species-dependent; do not treat every stated normality as chloride molarity. A percentage without its concentration basis may be underdetermined.

Use source rounding and graphical resolution to judge agreement, without imposing a universal tolerance. Keep signs and significant precision defensible. A printed 0.3 V or digitized coordinate near 0.30 V does not establish hundredth-millivolt agreement with a many-decimal CSV number. Preserve bounds, censoring, error bars and source statistical roles; comparing compatible numbers does not prove compatible statistical meanings. If the target or supporting-variable conversion cannot be justified, report the limitation instead of silently rejecting or confirming the match.
