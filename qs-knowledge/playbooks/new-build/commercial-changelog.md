# Commercial New Build Playbook - Changelog

## [2.0.0] - 2024-12-10

### Added - Standards-Keeper Agent Review
- **21 comprehensive phases** with 150+ measurement tasks
- **DQSRules** (Dell QS Rules) integrated for specific measurement methodology
- **DBRules** (Dell Builder Rules) for construction-specific approaches
- Each task includes: item, unit, measurement_rule, rule_detail, drawings
- Phase IDs (P01-P21) and Step IDs for tracking
- Task IDs for granular progress monitoring
- Dependencies between steps and phases
- Builder logic explanations for construction sequence
- Autonomy levels per phase (level_1_suggest, level_2_confirm, level_3_notify)
- Commercial-specific items: urinals, suspended ceilings, fire services, accessibility
- Learning mode hooks for improvement tracking
- Output requirements pointing to "Final Bills of Quantities/" folder
- Reference to QSPlus_Export_Module.py for BOQ exports

### Source Documents
- Reference/playbook-example.yaml (structure)
- Reference/QS-Task-Template.md (tasks and measurement rules)

### Phases Included
1. Foundations (site prep, excavation, concrete, brickwork)
2. Reinforced Concrete Structure (columns, beams, slabs)
3. Brickwork Structure (external masonry)
4. Surface Bed Construction (sub-base, concrete, finishes)
5. Roofs and Rainwater (structure, covering, gutters)
6. External Finishes
7. Internal Floor Finishes
8. Internal Wall Finishes
9. Ceilings
10. Doors (installation and adjustments)
11. Windows (installation and adjustments)
12. Joinery Fittings
13. Sundries
14. Plumbing and Drainage
15. Fire Services (extinguishers, hose reels, hydrants)
16. Sundry Metalwork
17. External Works
18. Builders Work to Specialists
19. Electrical Installation
20. Preliminaries
21. Health and Safety

---

## [1.0.0] - 2024-12-10

### Added
- Initial playbook creation
- Basic phase structure defined
