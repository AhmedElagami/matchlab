## Testing Philosophy

All testers start with a **clean environment** containing only an admin user.
Test data is **generated on demand** for each testing scenario to ensure:
- Reproducible results
- Isolated test cases
- No data contamination between testers
- Deterministic testing conditions

## Environment Reset

To reset to a clean testing state:
```bash
cd /home/ubuntu/matchlab
./scripts/reset_testing_env.sh
```

This removes all data and provides a clean database with only the admin user.

## Dataset Generation

Each tester has specific dataset generation capabilities:
- **Tester A**: Uses existing fixtures in `fixtures/` directory
- **Tester B**: Can create failure scenario datasets manually or adapt existing ones
- **Tester C**: Uses existing ambiguous match data or creates override test cases
- **Tester D**: Uses CSV import functionality for participant data generation
- **Tester E**: Uses `artifacts/datasets/generate_E_dataset.py` for scale testing