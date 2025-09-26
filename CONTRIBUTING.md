# 🤝 Contributing Guide

Thanks for considering a contribution! This document outlines a lightweight process to keep quality high and velocity fast.

## 1. Ways to Contribute
- Bug fixes
- Documentation improvements (README, docs/*)
- (Future) Test coverage
- New features (open an issue first for larger ideas)
- Refactoring / performance improvements

## 2. Development Setup
1. Fork & clone the repo.
2. Create a virtual environment & install deps:
   ```sh
   pip install -r requirements.txt
   ```
3. Run migrations & (optionally) import seed data:
   ```sh
   python manage.py migrate
   python manage.py import_data
   ```
4. Run server:
   ```sh
   python manage.py runserver
   ```

## 3. Branching Model
Use descriptive feature branches: `feat/search-pagination`, `fix/review-npe`, `docs/architecture-diagram`.

## 4. Commit Style
Keep commits small & focused. Conventional style (optional but encouraged):
```
feat: add review approval panel filters
fix: handle empty query in search view
chore: bump dependency versions
docs: expand architecture section
```

## 5. Code Standards (Initial)
- Python 3.12
- Prefer explicitness over cleverness
- Add docstrings for non-trivial functions/classes
- Handle edge cases (empty query, missing FK, etc.)
- Keep functions small; extract helpers when complexity grows

## 6. Testing (Deferred)
Automated tests are not yet part of the repository while core functionality is still evolving. Once introduced, guidelines will cover:
- Unit tests for models & utilities
- View / integration tests (search, review submission, moderation)
- Data pipeline validation (import & cleaning)

Planned structure (placeholder):
```
tests/
   test_models.py
   test_search.py
   test_review_flow.py
```

Until then, please describe manual verification steps in your PR description.

## 7. Pull Request Checklist
- [ ] Includes a clear summary & motivation
- [ ] (Future) Adds/updates tests (or explains why not applicable)
- [ ] (Future) Passes test suite locally
- [ ] No unrelated formatting-only changes
- [ ] Documentation updated (if user-facing change)

## 8. Reporting Issues
Include:
- Reproduction steps
- Expected vs actual behavior
- Environment details (OS, Python version)
- Logs / traceback (if applicable)

## 9. Roadmap Reference
See README "Future Enhancements" section. Propose additions via issue if needed.

## 10. License & Attribution
If/when a license file is added (e.g., MIT), contributions will be under that license. Make sure you have rights to any code you submit.

---
Thanks again—your improvements help make the project more useful for everyone! 🚀
