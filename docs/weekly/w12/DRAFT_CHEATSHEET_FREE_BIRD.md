# Draft cheat sheet: "The Free Bird" (Thanksgiving 2026: CHI@DET, PHI@DAL, KC@BUF)

**Source.** APEX weekly engine, 2026 week 12, market track. 20,000 joint simulations per game.
- **Anchored** columns (first) use the DECISIONS #91 market anchor: book lines snapshot 2026-11-25 18:54Z, 6 books. These are early-line anchored, not the T-2h snapshot.
- **Raw** columns are the same engine without lines.
- Manual-out: `w11_manual_out.py`, two passes, 196 rows. No status overlay; the nflverse W12 injury report governs.
- Per #91, the anchored numbers are the better projections: rec yds MAE -0.32, TD log loss -11%, DK-point MAE -0.08 in the 2023-25 backtest.

**Scoring.** 0.5/rec, 0.1/rush+rec yd, 6/TD, 0.04/pass yd, 4/pass TD, -1/INT, -2/fumble lost. 2-pt conversions are not simulated (worth about +0.1 to +0.2 pts for top players).
- **Mean** is unconditional: an inactive player scores 0.
- **P(top 12)** and **P(top 3)** are the share of simulations in which the player is among the 12 (or 3) highest scorers of the 3-game slate.
- **r with own QB** is the simulated correlation of his points with his starting QB's.

**Roster.** QB, RB, WR, WR, TE, FLEX (RB/WR/TE). 6 rounds, so every pick starts. About 30,000 entrants and top-heavy prizes: you are drafting for P(top 3), not for the mean.

## Rankings (top 45 by anchored mean)

| # | Player | Pos (rank) | Team | p_active | **Mean** | Median | P90 | P(top 12) | P(top 3) | r with own QB | Raw mean | Raw P90 | Raw P(top 12) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Jahmyr Gibbs | RB1 | DET | 1.00 | **21.8** | 20.7 | 34.1 | 0.80 | 0.38 | 0.08 | 20.9 | 33.1 | 0.80 |
| 2 | Caleb Williams | QB1 | CHI | 1.00 | **20.0** | 19.3 | 30.2 | 0.79 | 0.30 |  | 17.2 | 27.3 | 0.69 |
| 3 | Josh Allen | QB2 | BUF | 1.00 | **19.6** | 19.0 | 29.1 | 0.77 | 0.27 |  | 16.4 | 25.9 | 0.65 |
| 4 | Dak Prescott | QB3 | DAL | 0.98 | **19.2** | 18.8 | 29.9 | 0.74 | 0.27 |  | 18.4 | 29.1 | 0.75 |
| 5 | Jared Goff | QB4 | DET | 1.00 | **18.7** | 18.0 | 28.6 | 0.72 | 0.23 |  | 17.1 | 27.2 | 0.69 |
| 6 | CeeDee Lamb | WR1 | DAL | 1.00 | **17.3** | 16.2 | 27.9 | 0.62 | 0.19 | 0.52 | 15.7 | 26.4 | 0.58 |
| 7 | Patrick Mahomes | QB5 | KC | 0.98 | **17.0** | 16.5 | 27.0 | 0.64 | 0.18 |  | 15.6 | 25.2 | 0.62 |
| 8 | Joe Milton III | QB6 | PHI | 1.00 | **16.9** | 16.2 | 26.0 | 0.63 | 0.16 |  | 15.0 | 23.8 | 0.58 |
| 9 | Emmett Johnson | RB2 | KC | 1.00 | **16.2** | 16.0 | 22.9 | 0.63 | 0.10 | 0.10 | 7.6 | 14.2 | 0.13 |
| 10 | Javonte Williams | RB3 | DAL | 1.00 | **15.8** | 14.6 | 27.3 | 0.53 | 0.17 | 0.01 | 18.7 | 30.2 | 0.72 |
| 11 | Amon-Ra St. Brown | WR2 | DET | 1.00 | **15.5** | 14.6 | 25.2 | 0.53 | 0.12 | 0.53 | 13.3 | 23.1 | 0.45 |
| 12 | James Cook | RB4 | BUF | 1.00 | **14.5** | 13.2 | 24.9 | 0.46 | 0.13 | 0.02 | 15.4 | 26.1 | 0.56 |
| 13 | George Pickens | WR3 | DAL | 1.00 | **13.4** | 12.6 | 22.7 | 0.41 | 0.07 | 0.43 | 12.0 | 21.3 | 0.38 |
| 14 | D'Andre Swift | RB5 | CHI | 1.00 | **12.3** | 11.3 | 21.7 | 0.35 | 0.07 | 0.02 | 13.4 | 22.9 | 0.47 |
| 15 | Saquon Barkley | RB6 | PHI | 1.00 | **12.0** | 11.3 | 19.7 | 0.32 | 0.04 | 0.03 | 9.7 | 17.6 | 0.25 |
| 16 | Luther Burden III | WR4 | CHI | 1.00 | **11.7** | 10.8 | 20.1 | 0.30 | 0.04 | 0.44 | 10.4 | 18.8 | 0.28 |
| 17 | DeVonta Smith | WR5 | PHI | 0.99 | **11.5** | 10.6 | 19.7 | 0.29 | 0.04 | 0.44 | 10.4 | 18.6 | 0.28 |
| 18 | Colston Loveland | TE1 | CHI | 1.00 | **10.6** | 9.8 | 18.3 | 0.24 | 0.02 | 0.42 | 9.0 | 16.7 | 0.21 |
| 19 | Jameson Williams | WR6 | DET | 1.00 | **10.0** | 9.0 | 18.4 | 0.22 | 0.03 | 0.45 | 8.8 | 17.2 | 0.21 |
| 20 | Kenneth Walker III | RB7 | KC | 1.00 | **9.6** | 8.9 | 17.1 | 0.20 | 0.02 | 0.10 | 13.9 | 23.2 | 0.49 |
| 21 | Rome Odunze | WR7 | CHI | 1.00 | **9.5** | 8.6 | 17.7 | 0.20 | 0.03 | 0.45 | 9.3 | 17.6 | 0.23 |
| 22 | Sam LaPorta | TE2 | DET | 0.99 | **9.3** | 8.3 | 17.4 | 0.19 | 0.02 | 0.43 | 9.9 | 18.3 | 0.26 |
| 23 | DJ Moore | WR8 | BUF | 1.00 | **8.9** | 8.0 | 16.3 | 0.16 | 0.01 | 0.35 | 8.0 | 15.3 | 0.16 |
| 24 | Travis Kelce | TE3 | KC | 1.00 | **8.9** | 8.0 | 16.4 | 0.16 | 0.02 | 0.37 | 8.5 | 15.9 | 0.18 |
| 25 | Rashee Rice | WR9 | KC | 0.90 | **8.1** | 7.4 | 15.9 | 0.15 | 0.01 | 0.32 | 7.7 | 15.5 | 0.17 |
| 26 | Kyle Monangai | RB8 | CHI | 1.00 | **7.8** | 6.8 | 14.9 | 0.12 | 0.01 | 0.00 | 7.9 | 15.1 | 0.16 |
| 27 | Khalil Shakir | WR10 | BUF | 1.00 | **7.7** | 6.8 | 14.7 | 0.11 | 0.01 | 0.33 | 7.3 | 14.2 | 0.13 |
| 28 | Josh Downs | WR11 | KC | 1.00 | **7.4** | 6.4 | 14.2 | 0.10 | 0.01 | 0.36 | 6.9 | 13.7 | 0.11 |
| 29 | Dalton Kincaid | TE4 | BUF | 0.98 | **7.2** | 6.4 | 13.7 | 0.09 | 0.01 | 0.30 | 6.3 | 12.6 | 0.09 |
| 30 | Ryan Flournoy | WR12 | DAL | 1.00 | **6.5** | 5.6 | 13.1 | 0.08 | 0.00 | 0.33 | 6.4 | 13.2 | 0.10 |
| 31 | Dallas Goedert | TE5 | PHI | 0.99 | **6.4** | 5.6 | 12.4 | 0.06 | 0.00 | 0.33 | 5.7 | 11.4 | 0.06 |
| 32 | Makai Lemon | WR13 | PHI | 1.00 | **6.3** | 5.4 | 12.2 | 0.06 | 0.00 | 0.34 | 6.5 | 12.7 | 0.09 |
| 33 | Kalif Raymond | WR14 | CHI | 1.00 | **5.8** | 4.9 | 11.9 | 0.05 | 0.00 | 0.33 | 5.9 | 12.1 | 0.07 |
| 34 | Darius Cooper | WR15 | PHI | 1.00 | **5.4** | 4.4 | 11.2 | 0.04 | 0.00 | 0.32 | 5.3 | 11.4 | 0.06 |
| 35 | Keon Coleman | WR16 | BUF | 1.00 | **5.0** | 4.1 | 10.7 | 0.04 | 0.00 | 0.29 | 4.9 | 10.5 | 0.04 |
| 36 | Xavier Worthy | WR17 | KC | 1.00 | **5.0** | 4.0 | 10.9 | 0.04 | 0.00 | 0.32 | 5.9 | 12.2 | 0.08 |
| 37 | Isaac TeSlaa | WR18 | DET | 1.00 | **4.3** | 3.3 | 10.0 | 0.03 | 0.00 | 0.31 | 3.9 | 9.5 | 0.03 |
| 38 | Will Shipley | RB9 | PHI | 0.98 | **4.1** | 3.2 | 8.7 | 0.01 | 0.00 | 0.06 | 3.9 | 8.7 | 0.02 |
| 39 | Ty Johnson | RB10 | BUF | 0.94 | **3.8** | 3.0 | 8.4 | 0.01 | 0.00 | 0.14 | 3.5 | 8.0 | 0.02 |
| 40 | Brevyn Spann-Ford | TE6 | DAL | 1.00 | **3.6** | 2.7 | 8.5 | 0.01 | 0.00 | 0.19 | 2.8 | 7.1 | 0.01 |
| 41 | Sione Vaki | RB11 | DET | 1.00 | **3.6** | 2.6 | 8.3 | 0.01 | 0.00 | 0.05 | 3.7 | 8.4 | 0.02 |
| 42 | Dawson Knox | TE7 | BUF | 1.00 | **3.3** | 2.3 | 7.9 | 0.01 | 0.00 | 0.23 | 3.3 | 7.8 | 0.01 |
| 43 | Jake Ferguson | TE8 | DAL | 0.63 | **3.2** | 1.4 | 9.2 | 0.02 | 0.00 | 0.15 | 2.6 | 7.8 | 0.02 |
| 44 | Noah Gray | TE9 | KC | 0.99 | **3.1** | 2.3 | 7.6 | 0.01 | 0.00 | 0.23 | 3.2 | 7.8 | 0.01 |
| 45 | Zavion Thomas | WR19 | CHI | 1.00 | **2.9** | 2.0 | 7.2 | 0.01 | 0.00 | 0.19 | 2.5 | 6.4 | 0.01 |

## How to draft it

1. **Gibbs is the 1.01.** He is the highest mean (21.8), the highest P(top 3) (0.38), and the steepest position drop-off on the slate: RB1 21.8 vs RB5 12.4.
2. **QB is flat; wait on it.**
   - Six QBs fit between 20.0 and 16.9. The QB1 to QB6 gap (3.1 pts) is smaller than the gap between WR1 Lamb and WR3 Pickens (3.8).
   - QBs rank high on P(top 12) because they score every game, but you start exactly one.
   - Take Gibbs or Lamb or St. Brown first, then the QB who stacks with your WR.
3. **WR tiers:** Lamb (17.3) / St. Brown (15.5) / Pickens (13.4) / Burden, D. Smith (11.5-11.7) / J. Williams, Odunze (about 10). After about 10 pts the tier is wide and flat: those are your round 4-6 FLEX candidates.
4. **TE:**
   - Loveland (10.6, the market is higher on him than the raw engine), LaPorta (9.3) and Kelce (8.9) are one tier.
   - Kincaid (7.2) and Goedert (6.4) are the floor.
   - Do not take TE before round 3 unless the Loveland stack with Williams is your build.
5. **RB2 / FLEX value:**
   - **Emmett Johnson (KC) is the biggest market-vs-engine disagreement on the slate.** Anchored he is 16.2 (raw 7.6): the books price him as KC's lead back (81.5 rush yds, -160 to score). Walker drops to 9.6 (raw 13.9; he is listed Limited and has no posted yardage line).
   - The anchored sheet trusts the market; the #91 backtest says that is right more often than not. If you believe the engine's role read instead, Walker is the value.
   - Javonte Williams (15.8) and Cook (14.5) are steadier RB2s. Barkley's anchored 12.0 is +2.2 over raw.
6. **Injury flags:** Rashee Rice p_active 0.90; Jake Ferguson 0.63 (his P90 is propped up by the games he plays).

## Stacking (from the anchored simulations)

- **QB plus his WR1/TE is the only strong correlation:** r = +0.4 to +0.5.
  - Goff-St. Brown +0.53, Prescott-Lamb +0.52, Williams-Odunze/Burden/Loveland +0.42 to +0.45.
  - Prescott-Pickens +0.43, Milton-D. Smith +0.44, Mahomes-Kelce +0.37, Allen-Moore +0.35.
  - A QB with his own RB is about 0 (+0.01 to +0.10).
- **Bring-backs are about uncorrelated in the engine:** a QB with the opposing WR1/RB is r = -0.02 to +0.07.
  - The engine ties the two offenses together only through the game environment, so it likely understates real shootout correlation.
  - Treat a bring-back as a slight tiebreaker, not a reason to reach.
- **Best one-game builds for a top-heavy field:**
  - Prescott + Lamb (+ Pickens): the highest-ceiling pass stack. Lamb's P90 is 27.9.
  - Goff + St. Brown with Gibbs: the same-team RB adds no correlation but is the slate's best player.
  - Williams + Odunze/Loveland: the cheapest QB1 stack by draft position.
- **Leverage:** with about 30,000 entrants, the most popular build will be Gibbs + Lamb + a top QB. A Johnson (KC) or Loveland pick is where the anchored sheet differs from consensus-style rankings.

*Same inputs as the anchored W12 market freeze. Not betting advice. Anchored and raw tables: `var/ro/draft_free_bird_anch.csv` and `var/ro/draft_free_bird_raw.csv` (not committed).*

## Update 2026-11-26 16:01Z (lines 2 hours before kickoff, official Thursday injury report)

Re-anchored to the 16:01Z lines. The nflverse Thursday report is now in, and it confirms the Wednesday designations: Walker (KC), Ferguson and Mingo (DAL), and R. Johnson (CHI) are Out; Kincaid and N. Gray are Questionable. Run: `runs/weekly/2026_w12_market_20261126T160705Z`.

- **Rankings above stand.** The top-12 set is unchanged, and every move is 1.9 points or less.
- **Emmett Johnson (KC): 16.2 -> 17.7**, ranked 6th overall (was 9th). Walker's Out designation confirms the market read.
- **Dalton Kincaid (BUF): 7.2 -> 5.3.** He is Questionable (p_active 0.74) and drops below Goedert. TE order is now Loveland / LaPorta / Kelce, then a gap.
- **Small risers:** Gibbs 22.2, C. Williams 20.3, Prescott 19.6 (now QB2), Milton 17.3, Cook 15.1.
