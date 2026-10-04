---
name: injury-update
description: Refresh availability for Friday/Saturday/Sunday reruns and reconcile NFL report vs DraftKings status conflicts.
---
# Injury update

1. `fetch` again (nflverse injuries and depth charts update through the week).
2. List every Out/Doubtful/Questionable skill player and every QB1 change; show the model's p_active next to the report status.
3. DraftKings status lags the NFL report; the NFL report governs. Flag conflicts, never silently trust DK.
4. Sunday: official inactives land about 90 minutes before each window. If nflverse has not published them, say so and rerun only the affected games with manual overrides recorded in the run notes.
