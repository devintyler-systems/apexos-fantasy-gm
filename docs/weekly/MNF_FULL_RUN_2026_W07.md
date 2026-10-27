# Week 7 Monday night, DAL@PHI: every priced line with a Play/Pass label

Inputs: operator-read NFL.com official inactives (DAL: Demercado, Turpin, Shelton, Wheat, Winters; PHI: Payton, D. Smith, Wicks, Majors, N. Smith, Carter II), operator workbook prices (22:50Z, nine books), engine run `2026_w07_{market,model}_20261026T23*` (mon5).
Confidence = book de-vigged probability + 0.5 x (model - book) (DECISIONS #53). EV is at the best price across the books. Label rules: PLAY needs EV of 4% (8% for touchdowns), confidence of 52% or more, model within 15 points of the book, no flag from the audits; rush-yard lines and passing yards are always PASS (interim rule, Week 7 postmortem); red-team pulls and downgrades are PASS.
The model gives Saquon Barkley 6.8 carries against a 15.5 book line (a returning-back allocation artifact), so every PHI backfield line is PASS.

| Player | Market | Side/line | Confidence | Model / book | Best price | EV | Label | Reason |
|---|---|---|---|---|---|---|---|---|
| Brevyn Spann-Ford DAL | rec | U 1.5 | 63% | 71 / 55 | -130 Bovada | +12% | **PASS** | red-team pull |
| Brevyn Spann-Ford DAL | rec_yds | U 13.5 | 60% | 70 / 50 | -110 Bovada | +14% | **PASS** | red-team pull |
| Brevyn Spann-Ford DAL | anytime_td | yes | 9% | 5 / 12 | +650 DraftKings | -33% | **PASS** | model above 85% ceiling |
| CeeDee Lamb DAL | rec | O 6.5 | 52% | 49 / 54 | -133 DraftKings | -10% | **PASS** | red-team downgrade |
| CeeDee Lamb DAL | rec_yds | U 79.5 | 52% | 54 / 49 | -105 BetMGM | +1% | **PASS** | red-team downgrade |
| CeeDee Lamb DAL | anytime_td | yes | 37% | 35 / 40 | +130 FanDuel | -14% | **PASS** | no edge at the best price (EV -14%) |
| Dak Prescott DAL | pass_att | O 35.5 | 58% | 64 / 51 | -115 Bovada | +8% | **PLAY** | EV +8% at best price |
| Dak Prescott DAL | pass_cmp | U 24.5 | 55% | 57 / 52 | -124 DraftKings | -1% | **PASS** | no edge at the best price (EV -1%) |
| Dak Prescott DAL | pass_yds | U 262.5 | 53% | 57 / 50 | -111 DraftKings | +2% | **PASS** | model weaker than books on pass yards (W7 Brier .297 vs .251) |
| Dak Prescott DAL | rush_yds | U 9.5 | 57% | 65 / 49 | -105 DraftKings | +12% | **PASS** | red-team pull |
| Dak Prescott DAL | anytime_td | yes | 14% | 15 / 13 | +650 BetRivers | +5% | **PASS** | model above 85% ceiling |
| George Pickens DAL | rec | O 4.5 | 59% | 62 / 56 | -138 DraftKings | +1% | **PASS** | no edge at the best price (EV +1%) |
| George Pickens DAL | rec_yds | O 64.5 | 50% | 51 / 50 | -110 BetMGM | -4% | **PASS** | no edge at the best price (EV -4%) |
| George Pickens DAL | anytime_td | yes | 30% | 27 / 33 | +180 FanDuel | -15% | **PASS** | no edge at the best price (EV -15%) |
| Hunter Luepke DAL | anytime_td | yes | 6% | 6 / 7 | +1400 DraftKings | -4% | **PASS** | model above 85% ceiling |
| Jake Ferguson DAL | rec | O 2.5 | 59% | 68 / 49 | +100 BetMGM | +17% | **PASS** | model 15+ points from book: unreliable |
| Jake Ferguson DAL | rec_yds | O 17.5 | 60% | 70 / 50 | -106 BetOnline.ag | +17% | **PASS** | model 15+ points from book: unreliable |
| Jake Ferguson DAL | anytime_td | yes | 21% | 18 / 24 | +295 BetRivers | -17% | **PASS** | no edge at the best price (EV -17%) |
| Javonte Williams DAL | rush_att | U 16.5 | 54% | 58 / 50 | -106 DraftKings | +4% | **PASS** | red-team downgrade |
| Javonte Williams DAL | rush_yds | U 62.5 | 53% | 56 / 50 | -113 FanDuel | -0% | **PASS** | rush-yard lines are LEAN at most (interim rule) |
| Javonte Williams DAL | rec | U 2.5 | 53% | 50 / 56 | -140 FanDuel | -9% | **PASS** | no edge at the best price (EV -9%) |
| Javonte Williams DAL | rec_yds | O 12.5 | 53% | 55 / 50 | -111 DraftKings | -0% | **PASS** | no edge at the best price (EV -0%) |
| Javonte Williams DAL | anytime_td | yes | 60% | 64 / 56 | -150 FanDuel | +0% | **PASS** | red-team downgrade |
| Jonathan Mingo DAL | anytime_td | yes | 6% | 4 / 8 | +1100 DraftKings | -25% | **PASS** | model above 85% ceiling |
| Luke Schoonmaker DAL | anytime_td | yes | 4% | 2 / 6 | +1700 BetMGM | -26% | **PASS** | model above 85% ceiling |
| Ryan Flournoy DAL | rec | U 3.5 | 54% | 55 / 52 | -123 DraftKings | -3% | **PASS** | no edge at the best price (EV -3%) |
| Ryan Flournoy DAL | rec_yds | U 35.5 | 51% | 53 / 50 | -109 DraftKings | -2% | **PASS** | no edge at the best price (EV -2%) |
| Ryan Flournoy DAL | anytime_td | yes | 21% | 22 / 19 | +380 DraftKings | -1% | **PASS** | no edge at the best price (EV -1%) |
| Tyler Goodson DAL | rush_yds | U 13.5 | 58% | 65 / 50 | -111 DraftKings | +9% | **PASS** | rush-yard lines are LEAN at most (interim rule) |
| Tyler Goodson DAL | anytime_td | yes | 11% | 13 / 9 | +1100 DraftKings | +29% | **PASS** | model above 85% ceiling |
| Britain Covey PHI | anytime_td | yes | 3% | 1 / 4 | +2500 BetMGM | -31% | **PASS** | model above 85% ceiling |
| Dallas Goedert PHI | rec | U 5.5 | 58% | 61 / 55 | -123 BetOnline.ag | +5% | **PLAY** | EV +5% at best price |
| Dallas Goedert PHI | rec_yds | U 49.5 | 52% | 55 / 50 | -113 FanDuel | -1% | **PASS** | no edge at the best price (EV -1%) |
| Dallas Goedert PHI | anytime_td | yes | 30% | 29 / 32 | +190 BetMGM | -12% | **PASS** | no edge at the best price (EV -12%) |
| Dameon Pierce PHI | rush_att | O 5.5 | 74% | 96 / 52 | -122 DraftKings | +34% | **PASS** | model 15+ points from book: unreliable |
| Dameon Pierce PHI | rush_yds | O 18.5 | 69% | 87 / 51 | -113 DraftKings | +30% | **PASS** | rush-yard lines are LEAN at most (interim rule) |
| Dameon Pierce PHI | rec_yds | O 1.5 | 70% | 91 / 48 | +102 FanDuel | +41% | **PASS** | model 15+ points from book: unreliable |
| Dameon Pierce PHI | anytime_td | yes | 25% | 35 / 15 | +550 FanDuel | +61% | **PASS** | model 15+ points from book: unreliable |
| Darius Cooper PHI | rec | U 3.5 | 74% | 92 / 56 | -140 BetMGM | +26% | **PASS** | model 15+ points from book: unreliable |
| Darius Cooper PHI | rec_yds | U 39.5 | 66% | 83 / 50 | -112 DraftKings | +25% | **PASS** | model 15+ points from book: unreliable |
| Darius Cooper PHI | anytime_td | yes | 24% | 22 / 25 | +285 DraftKings | -9% | **PASS** | red-team downgrade |
| Elijah Moore PHI | rec | U 1.5 | 67% | 83 / 52 | -110 DraftKings | +29% | **PASS** | model 15+ points from book: unreliable |
| Elijah Moore PHI | rec_yds | U 9.5 | 59% | 68 / 49 | -110 BetMGM | +12% | **PASS** | model 15+ points from book: unreliable |
| Elijah Moore PHI | anytime_td | yes | 6% | 4 / 8 | +1450 BetMGM | -7% | **PASS** | model above 85% ceiling |
| Johnny Mundt PHI | anytime_td | yes | 5% | 4 / 5 | +2500 FanDuel | +18% | **PASS** | model above 85% ceiling |
| Makai Lemon PHI | rec | O 3.5 | 56% | 51 / 61 | -182 DraftKings | -13% | **PASS** | no edge at the best price (EV -13%) |
| Makai Lemon PHI | rec_yds | U 38.5 | 52% | 55 / 49 | +100 Bovada | +4% | **PLAY** | EV +4% at best price |
| Makai Lemon PHI | anytime_td | yes | 21% | 19 / 22 | +325 BetMGM | -12% | **PASS** | no edge at the best price (EV -12%) |
| Saquon Barkley PHI | rush_att | U 15.5 | 75% | 99 / 51 | -114 DraftKings | +41% | **PASS** | model 15+ points from book: unreliable |
| Saquon Barkley PHI | rush_yds | U 63.5 | 70% | 90 / 50 | -110 BetOnline.ag | +33% | **PASS** | rush-yard lines are LEAN at most (interim rule) |
| Saquon Barkley PHI | rec | U 2.5 | 59% | 66 / 52 | -119 BetOnline.ag | +9% | **PASS** | model 15+ points from book: unreliable |
| Saquon Barkley PHI | rec_yds | U 13.5 | 52% | 56 / 49 | -109 BetRivers | +1% | **PASS** | no edge at the best price (EV +1%) |
| Saquon Barkley PHI | anytime_td | yes | 33% | 23 / 44 | +110 FanDuel | -30% | **PASS** | model 15+ points from book: unreliable |
| Tanner McKee PHI | pass_att | U 33.5 | 53% | 55 / 50 | -106 DraftKings | +3% | **PASS** | no edge at the best price (EV +3%) |
| Tanner McKee PHI | pass_cmp | O 20.5 | 50% | 50 / 50 | -104 BetRivers | -1% | **PASS** | no edge at the best price (EV -1%) |
| Tanner McKee PHI | pass_yds | O 198.5 | 50% | 51 / 50 | -113 FanDuel | -5% | **PASS** | model weaker than books on pass yards (W7 Brier .297 vs .251) |
| Tanner McKee PHI | rush_yds | U 4.5 | 51% | 53 / 50 | -113 FanDuel | -3% | **PASS** | rush-yard lines are LEAN at most (interim rule) |
| Tanner McKee PHI | anytime_td | yes | 7% | 5 / 10 | +1000 DraftKings | -19% | **PASS** | model above 85% ceiling |
