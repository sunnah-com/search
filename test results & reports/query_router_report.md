# Query Router: Reference Lookup vs Lexical BM25

**Date:** 2026-06-02  
**API:** http://localhost:5001  

For each `collection number` query, the router now does a direct filter lookup.
The **Lexical (pre-router)** column shows what BM25 would have returned — the
correct hadith may not be first, or may not appear at all in top 10.

---
## Bukhari 1  —  `bukhari 1`

### Reference route  *(route: reference)*
**bukhari:1** — Narrated 'Umar bin Al-Khattab: <p>       I heard Allah's Apostle saying, "The reward of deeds depends upon the       int…
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 bukhari:1** ← target  —  Narrated 'Umar bin Al-Khattab: <p>       I heard Allah's Apostle saying, "The reward of deeds depends upon the       int…

---
## Bukhari 7563  —  `bukhari 7563`

### Reference route  *(route: reference)*
**bukhari:7563** — <p> Narrated Abu Huraira:  <p>The Prophet said, "(There are) two words which are dear to the Beneficent (Allah) and very…
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 bukhari:7563** ← target  —  <p> Narrated Abu Huraira:  <p>The Prophet said, "(There are) two words which are dear to the Beneficent (Allah) and very…

---
## Muslim 1  —  `muslim 1`

### Reference route  *(route: reference)*
**muslim:1** — Abū Bakr ibn Abī Shaybah narrated to us that Ghundar narrated to us, on authority of Shu’bah; and Muhammad bin ul-Muthan…
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 muslim:1** ← target  —  Abū Bakr ibn Abī Shaybah narrated to us that Ghundar narrated to us, on authority of Shu’bah; and Muhammad bin ul-Muthan…

---
## Muslim 2363  —  `muslim 2363`

### Reference route  *(route: reference)*
**muslim:2363** — <p> Anas reported that Allah's Messenger (may peace be upon him) happened to pass by the people who had been busy in gra…
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 muslim:2363** ← target  —  <p> Anas reported that Allah's Messenger (may peace be upon him) happened to pass by the people who had been busy in gra…

---
## Nasai 1  —  `nasai 1`

### Reference route  *(route: reference)*
**nasai:1** — It was narrated from Abu Hurairah that the Prophet (PBUH) said: "When any one of you wakes from sleep, let him not dip h…
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 nasai:1** ← target  —  It was narrated from Abu Hurairah that the Prophet (PBUH) said: "When any one of you wakes from sleep, let him not dip h…

---
## Abu Dawud 1  —  `abudawud 1`

### Reference route  *(route: reference)*
**abudawud:1** — <p>  Narrated Mughirah ibn Shu'bah: </p>    <p>  When the Prophet (saws) went (outside) to relieve himself, he went to a…
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 abudawud:1** ← target  —  <p>  Narrated Mughirah ibn Shu'bah: </p>    <p>  When the Prophet (saws) went (outside) to relieve himself, he went to a…

---
## Ibn Majah 1  —  `ibnmajah 1`

### Reference route  *(route: reference)*
**ibnmajah:1** — Abu Hurairah narrated that: The Prophet said: "Whatever I have commanded you do it, and whatever I have forbidden you, r…
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 ibnmajah:1** ← target  —  Abu Hurairah narrated that: The Prophet said: "Whatever I have commanded you do it, and whatever I have forbidden you, r…

---
## Tirmidhi 1  —  `tirmidhi 1`

### Reference route  *(route: reference)*
**tirmidhi:1** — Ibn `Umar narrated that: the Prophet said: "Salat will not be accepted without purification, nor Charity from Ghulul."  …
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 tirmidhi:1** ← target  —  Ibn `Umar narrated that: the Prophet said: "Salat will not be accepted without purification, nor Charity from Ghulul."  …

---
## Malik 1  —  `malik 1`

### Reference route  *(route: reference)*
**malik:1** — <p> Yahya related to me from Malik that he heard that Luqman al-Hakim made his will and counselled his son, saying, "My …
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 malik:1** ← target  —  <p> Yahya related to me from Malik that he heard that Luqman al-Hakim made his will and counselled his son, saying, "My …
**👉 malik:1** ← target  —  <p> He said, "Yahya ibn Yahya al-Laythi related to me from Malik ibn Anas from Ibn Shihab that one day Umar ibn Abdal-Az…

---
## Nawawi 40 #1  —  `nawawi40 1`

### Reference route  *(route: reference)*
**forty:1** — The report is not like witnessing.
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 forty:1** ← target  —  The report is not like witnessing.
**👉 forty:1** ← target  —  <p>It is narrated on the authority of Amirul Mu'minin, Abu Hafs 'Umar bin al-Khattab (ra) who said:  I heard the Messeng…
**👉 forty:1** ← target  —  On the authority of Abu Hurayrah (may Allah be pleased with him), who said that the Messenger of Allah (PBUH) said: When…

---
## Nawawi 40 #40  —  `nawawi40 40`

### Reference route  *(route: reference)*
**forty:40** — Meetings are under trust.
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 forty:40** ← target  —  Meetings are under trust.
**👉 forty:40** ← target  —  <p>On the authority of Abdullah ibn Umar (may Allah be pleased with him), who said:  The Messenger of Allah (peace and…
**👉 forty:40** ← target  —  On the authority of Abu Sa'id al-Khudri (may Allah be pleased with him), who said that the Messenger of Allah (PBUH) sai…

---
## Forty #13  —  `forty 13`

### Reference route  *(route: reference)*
**forty:13** — A little that suffices is better than an abundance that distracts.
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 forty:13** ← target  —  A little that suffices is better than an abundance that distracts.
**👉 forty:13** ← target  —  <p>On the authority of Abu Hamzah Anas bin Malik (may Allah be pleased with him) — the servant of the Messenger of Allah…
**👉 forty:13** ← target  —  On the authority of Adiyy ibn Hatim (may Allah be pleased with him), who said: I was with the Messenger of Allah (may t…

---
## Riyad #1  —  `riyadussalihin 1`

### Reference route  *(route: reference)*
**riyadussalihin:1** — 'Umar bin Al-Khattab (May Allah be pleased with him), reported: The Messenger of Allah (PBUH) said, "The deeds are consi…
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 riyadussalihin:1** ← target  —  'Umar bin Al-Khattab (May Allah be pleased with him), reported: The Messenger of Allah (PBUH) said, "The deeds are consi…

---
## Mishkat 1  —  `mishkat 1`

### Reference route  *(route: reference)*
**mishkat:1** — ‘Umar b. al-Khattab, for whom God’s good pleasure is prayed, reported God’s Messenger, to whom may God’s blessings and s…
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 mishkat:1** ← target  —  ‘Umar b. al-Khattab, for whom God’s good pleasure is prayed, reported God’s Messenger, to whom may God’s blessings and s…

---
## Bulugh 1  —  `bulugh 1`

### Reference route  *(route: reference)*
**bulugh:1** — Narrated Abu Huraira:  Allah’s Messenger (saw) said regarding the sea, "It's water is purifying and its dead (animals) a…
Correct hadith: ✅ Yes

### Lexical BM25  *(pre-router behavior)*
**👉 bulugh:1** ← target  —  Narrated Abu Huraira:  Allah’s Messenger (saw) said regarding the sea, "It's water is purifying and its dead (animals) a…

---
## Summary

| Metric | Count |
|--------|-------|
| Queries tested | 15 |
| Reference route: correct hadith returned | 15/15 |
| Lexical BM25: target at rank 1 | 11/15 |
| Lexical BM25: target **not in top 10** | 0/15 |

The reference route is a deterministic filter (no scoring) — it either finds
the hadith or returns empty. Lexical BM25 uses `collection^2 + hadithNumber^2`
boosts but still competes with other term matches, so the target can be displaced.
