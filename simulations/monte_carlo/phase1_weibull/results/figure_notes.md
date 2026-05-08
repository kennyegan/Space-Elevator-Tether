# Weibull Extension — Figure Interpretation Notes

Drafting material for §5.2, §6.3, and §8.2.

## Figure 1: Reliability Surface by β

Shows the 10-year system survival probability P_sys(N, η_j) as a heatmap for each Weibull shape parameter β ∈ {1.0, 1.3, 1.5, 2.0, 2.5} at optimal inspection (cadence=1, p_det=0.995). As β increases from 1.0 (memoryless) to 2.5 (strong wear-out), the high-reliability region (green) contracts toward lower N and higher η_j, demonstrating that wear-out failure physics tightens the design envelope. The 0.995 and 0.999 contour lines shift visibly, quantifying the additional joint quality margin required to compensate for aging effects.

## Figure 2: P_sys vs β

Plots system survival probability against the Weibull shape parameter for four representative design points. The baseline optimistic case (N=83, η_j=0.95) maintains high reliability even at β=2.0, while the worst-case configuration (N=500, η_j=0.80) degrades sharply beyond β=1.5. This confirms that the modular architecture's reliability margin depends critically on the interaction between joint quality and aging severity — high segment counts amplify wear-out effects due to combinatorial exposure.

## Figure 3: β Threshold

For the optimistic design point (N=83), this figure maps each Weibull shape parameter to the minimum joint efficiency η_j required to maintain P_sys ≥ 0.995. At β=1.0 (memoryless), η_j ≈ 0.88 suffices; as β increases toward 2.5, the required η_j rises, potentially exceeding the current baseline of 0.95. This directly translates wear-out severity into a manufacturing quality target for joint qualification testing.

## Figure 4: MTTR Distribution by β

Compares the repair time distribution across Weibull shape parameters at the baseline configuration (N=18, η_j=0.95, cadence=1, p_det=0.995). The median MTTR and 5th/95th percentile range are shown. With stronger wear-out (higher β), failures cluster toward the end of the mission, potentially creating burst repair demands that stress logistics capacity despite the overall MTTR remaining below the 72-hour target.

## Figure 5: Inspection Cadence Sensitivity by β

Two-panel comparison (N=18 conservative, N=83 optimistic) showing how system reliability depends on inspection frequency under different wear-out assumptions. At β=1.0 (exponential), cadence has modest impact; at β≥2.0, the penalty for infrequent inspection steepens significantly because wear-out concentrates failures in time windows where prompt detection becomes critical. This reinforces the argument for autonomous NDE integration with every climber passage.

## Figure 6: Hazard Rate Tornado

Tornado diagram (log scale) showing the sensitivity of the full-scale mission-averaged hazard rate to ±40% perturbation of each input parameter. The activation energy Q dominates overwhelmingly, reflecting the exponential Arrhenius dependence — a 40% reduction in Q increases the hazard rate by ~7 orders of magnitude. Zone 3 temperature (T₃, where the majority of joints reside) ranks second, also via the exponential. The Weibull modulus m, volume ratio, and coupon rate contribute at most ~0.4 decades. This underscores that the single most critical parameter for the reliability prediction is the activation energy assumed for CNT joint degradation.

## Figure 7: Hazard Rate Spider Plot

Spider plot (log scale) showing λ_full/λ_baseline as a function of perturbation percentage. Q exhibits extreme nonlinearity — its curve spans ~7 orders of magnitude, confirming that the Arrhenius activation energy is the dominant source of uncertainty. Underestimating Q (lower activation barrier) is catastrophic for reliability; overestimating it is conservative. T₃ shows similar exponential sensitivity. The remaining parameters (m, V_ratio, λ_coupon) contribute at most half a decade, entering as power-law or linear factors. This plot makes the case that experimental determination of Q for CNT nanobonded joints is the single highest-priority measurement for reducing uncertainty in the reliability prediction.

