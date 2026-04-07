#!/bin/bash
# Organize figures into main/ (16), supplementary/ (17), and archive/ (orphaned)
# Filenames get prefixed with their figure number for easy sorting.
# Original files stay in place (symlinks) so existing code paths don't break.

cd "$(dirname "$0")"

# ── Main text (Fig. 1–16) ──
cp fig_taper_validation.pdf                 main/fig01_taper_validation.pdf
cp fig_design_envelope_comparison.pdf       main/fig02_design_envelope_comparison.pdf
cp fig_sigma_sensitivity.pdf                main/fig03_sigma_sensitivity.pdf
cp fig_reliability_merged.pdf               main/fig04_reliability_merged.pdf
cp fig_beta_threshold.pdf                   main/fig05_beta_threshold.pdf
cp fig_hazard_tornado.pdf                   main/fig06_hazard_tornado.pdf
cp fig_mttr_merged.pdf                      main/fig07_mttr_merged.pdf
cp fig_mttr_vs_depots.pdf                   main/fig08_mttr_vs_depots.pdf
cp fig_72h_achievability.pdf                main/fig09_72h_achievability.pdf
cp fig_modal_comparison.pdf                 main/fig10_modal_comparison.pdf
cp fig_displacement_envelopes_merged.pdf    main/fig11_displacement_envelopes_merged.pdf
cp fig_tension_perturbation.pdf             main/fig12_tension_perturbation.pdf
cp fig_resonance_scan.pdf                   main/fig13_resonance_scan.pdf
cp fig_npv_merged.pdf                       main/fig14_npv_merged.pdf
cp fig_cost_tornado.pdf                     main/fig15_cost_tornado.pdf
cp fig_depot_breakeven.pdf                  main/fig16_depot_breakeven.pdf

# ── Supplementary (Fig. S1–S17) ──
cp fig_psys_heatmap.pdf                     supplementary/figS01_psys_heatmap.pdf
cp fig_mttr_distribution.pdf                supplementary/figS02_mttr_distribution.pdf
cp fig_inspection_cadence.pdf               supplementary/figS03_inspection_cadence.pdf
cp fig_p_detection_impact.pdf               supplementary/figS04_p_detection_impact.pdf
cp fig_reliability_surface_by_beta.pdf      supplementary/figS05_reliability_surface_by_beta.pdf
cp fig_psys_vs_beta.pdf                     supplementary/figS06_psys_vs_beta.pdf
cp fig_mttr_by_beta.pdf                     supplementary/figS07_mttr_by_beta.pdf
cp fig_cadence_sensitivity_by_beta.pdf      supplementary/figS08_cadence_sensitivity_by_beta.pdf
cp fig_hazard_spider.pdf                    supplementary/figS09_hazard_spider.pdf
cp fig_longitudinal_envelope.pdf            supplementary/figS10_longitudinal_envelope.pdf
cp fig_transverse_envelope.pdf              supplementary/figS11_transverse_envelope.pdf
cp fig_waterfall_vrt.pdf                    supplementary/figS12_waterfall_vrt.pdf
cp fig_geo_time_history.pdf                 supplementary/figS13_geo_time_history.pdf
cp fig_safe_separation.pdf                  supplementary/figS14_safe_separation.pdf
cp fig_resonant_vs_offresonant.pdf          supplementary/figS15_resonant_vs_offresonant.pdf
cp fig_damping_sensitivity.pdf              supplementary/figS16_damping_sensitivity.pdf
cp fig_depot_placement_comparison.pdf       supplementary/figS17_depot_placement_comparison.pdf

# ── Archive (orphaned / superseded) ──
cp fig_depot_cost_tradespace.pdf            archive/fig_depot_cost_tradespace.pdf
cp fig_npv_crossover.pdf                    archive/fig_npv_crossover.pdf
cp fig_npv_with_depots.pdf                  archive/fig_npv_with_depots.pdf
cp fig_weibull_mttr_depot_shift.pdf         archive/fig_weibull_mttr_depot_shift.pdf

echo "Organized: 16 main, 17 supplementary, 4 archived"
