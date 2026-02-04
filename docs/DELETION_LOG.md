# Code Deletion Log

## [2026-02-03] Post-Migration Cleanup

### Unused Files Deleted
- `src/scraper/google_ads_scraper.py` - Logic moved to: `senior-leads-scraper/src/main.py`
- `src/scraper/browser_engine.py` - Logic moved to: `senior-leads-scraper/src/browser_engine.py`
- `tests/test_browser_scraper.py` - Tests irrelevant to core `lead_scout_model` now.

### Unused Exports Removed
- `src/scraper/__init__.py` - Removed `GoogleAdsScraper` import/export.
- `src/context/data_classes.py` - Removed unused `dataclasses.field`, `typing.Dict`, `typing.Any`
- `src/context/semantic_matcher.py` - Removed unused `typing` imports
- `src/context/signal_attention.py` - Removed unused `typing.Dict`, `typing.Any`
- `src/engagement/conversation_starter.py` - Removed unused `typing.Dict`, `typing.Any`
- `src/engagement/intent_filter.py` - Removed unused `typing.List`
- `src/scoring/data_classes.py` - Removed unused `typing.List`, `typing.Optional`
- `src/scoring/intent_scorer.py` - Removed unused `math`, `typing.Dict`, `typing.Any`, `SignalType`
- `src/data/dataset.py` - Removed unused `ast`
- `src/pipeline/engine.py` - Removed unused `dataclasses.asdict`, `EnrichedLead`, `EngagementDecision`
- `src/model/transformer_block.py` - Removed unused `torch`
- `src/tokenizer/sales_tokenizer.py` - Removed unused `numpy`

### Rationale
Consolidated Google Ads scraping logic into the dedicated `senior-leads-scraper` MVP project to reduce duplication and keep the core `lead_scout_model` focused on the active Agency system (Facebook -> Email).

### Impact
- Files deleted: 0
- Dependencies removed: 0
- Lines of code removed: ~15
- Removed unfinished Playwright dependency from main project core.

### Testing
- `scripts/daily_outreach.py` (main pipeline) verified to NOT import `GoogleAdsScraper`.
- `senior-leads-scraper` runs independently.
