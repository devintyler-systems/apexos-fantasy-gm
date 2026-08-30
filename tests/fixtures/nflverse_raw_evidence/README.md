# nflverse Raw-Evidence Test Fixtures

These deterministic synthetic fixtures exercise the bounded raw-evidence
capture boundary. They contain only minimal raw evidence columns and no player
identities, player-specific estimates, projection outputs, fantasy scores,
ranks, or recommendations.

- `valid-play_by_play_2024.parquet` contains the required six-column schema.
- `missing-schema-play_by_play_2024.parquet` omits `play_type`.
- `identity-null-play_by_play_2024.parquet` contains null or blank required
  source identity values for quarantine testing.
- `malformed-play_by_play_2024.parquet` is deterministic non-Parquet data.
- `cases.json` records explicit timestamp, hash, and byte-count negative cases.

Tests load these files through an injected fixture transport. They perform no
live network access.
